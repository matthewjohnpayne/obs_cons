'''
Code to look-for & fix, cross-file duplicates
I.e. observations which appear in multiple files under multiple designations

*** Do NOT run in the same way as the fix_desig / fix_prog routines ***

'''

# Third party imports
import sys, os
import glob
from collections import Mapping, Container, Counter, defaultdict
import subprocess

# Functions to find & fix cross-desig duplicates ...
def _get_filenames():
    ''' get a dict containing all the filenames we want to work with ...'''
    
    # Get filenames for num & unnum observations
    files_ = _get_numbered_filenames()
    files_.extend(_get_unnumbered_filenames())
    
    return files_
    
def _get_numbered_filenames():
    ''' get filenames for numbered observations (primary data files)'''

    filenames_to_ignore = ['unpub.num']

    # ------------ NUMBERED FILES ------------------
    # Primary, published files
    files_ = [_ for _ in glob.glob(f'/sa/mpn/N*dat', recursive=True) if _ not in filenames_to_ignore]
    
    # In-progress ( between monthly pubs) files are in different location ...
    # E.g. "tot.num", "pending.num", ..., ...
    files_.extend( [_ for _ in glob.glob(f'/sa/obs/*num', recursive=True) if _ not in filenames_to_ignore] )
    
    return files_
    
def _get_unnumbered_filenames(  ):
    ''' get filenames for unnumbered observations (primary data files)'''

    filenames_to_ignore = []

    # ---------------- UN-numbered FILES -----------
    files_ = []
    files_.extend( [_ for _ in glob.glob(f'/sa/mpu/*dat', recursive=True) if _ not in filenames_to_ignore] )
    files_.extend( [_ for _ in glob.glob(f'/sa/obs/*unn', recursive=True) if _ not in filenames_to_ignore] )

    return files_


def split_into_groups(filepath_list, group_size = 50 ):
    ''' Split files into "groups" of filenames'''
    group_dict = {}
    for i, filepath in enumerate(filepath_list):
        grp_num = 'Grp' + str(i // group_size)
        
        if grp_num not in group_dict:
            group_dict[grp_num] = []
            
        group_dict[grp_num].append(filepath)
    
    print(f"split_into_groups: N_groups = {len(group_dict)}, N_files = {len(filepath_list)}")
    return group_dict

def load_grp_obs(filepath_list):
    ''' load the contents of all files into a dict '''
    obs_dict = {}
    for i, fp in enumerate(filepath_list):
        #sprint(i, end=', ', flush=True )
        # Read the file contents into a dictionary
        with open(fp,'r') as fh:
            # NB: This will overwrite/ignore any duplicates that occur within the same file
            obs_dict[fp] = {line[15:56]:fp for line in fh if line[14] not in ['s','v']}
    return obs_dict

def find_duplicates(obs_dict):
    
    # We will read all data into a single big dictionary
    ALL = {}
    DUP = defaultdict(list)
    
    # Loop through all of the dictionaries that have been loaded
    for fp, fp_dict in obs_dict.items():

        # intersecn indicates duplicate obs80-bits
        intersecn = fp_dict.keys() & ALL.keys()

        # store duplicates with list of file-integers
        for k in intersecn:
            DUP[k].append(fp_dict[k])
            if isinstance(ALL[k], str):
                DUP[k].append(ALL[k])
            else:
                DUP[k].extend(ALL[k])
                
        # update the overall dictionary with local data
        ALL.update(fp_dict)
        
        # update the overall dictionary with the duplicates
        ALL.update(DUP)
        
    print(f'\t N_All= {len(ALL)}, N_Dup= {len(DUP)}')
    del ALL
    return DUP

def find_cross_desig_duplicates() :
    duplicates = {}
    dup_file_list = []
    
    # Get all filenames of "primary" data files
    filepath_list = _get_filenames()
    
    # Split files into "groups" of filenames
    group_dict = split_into_groups(filepath_list)
    
    # Loop over Groups
    grp_names = list(group_dict.keys())
    for i in range(len(grp_names)):
        for j in range(i+1,len(grp_names)):
            grp_i,grp_j = grp_names[i], grp_names[j]
            
            print(grp_i,grp_j,' ... loading...')

            # load the contents of all files in each grp into a dict
            obs_dict_grp = load_grp_obs( group_dict[grp_i] )
            obs_dict_grp.update( load_grp_obs( group_dict[grp_j] ) )
            print("\n N_loaded = ", len(obs_dict_grp) )
            
            # I don't think we need to bother finding duplicates within an individual group
            # Instead just find any duplicates anywhere across the loaded contents
            duplicated_obs80_dict = find_duplicates(obs_dict_grp)
            
            # The duplicate information returned above is a little sparse (obs80-only)
            # - Let's get all of the required data in a nice format ...
            duplicates[(grp_i,grp_j)] = get_required_data(duplicated_obs80_dict)

            # Record the duplicates
            dup_file_list.append( save_duplicates(i,j, duplicates[(grp_i,grp_j)]) )
            
        
    return dup_file_list , duplicates
        
def save_duplicates(i,j, duplicate_dict):
    print('save_duplicates:', i,j, len(duplicate_dict))
    dup_file = os.path.join(f'cross_des_duplicates_{i}_{j}.txt')
    with open( dup_file , 'w') as fh:
        for obs80bit, lst in duplicate_dict.items():
            for _ in lst:
                fh.write(f'{_}\n')
    print('\t'*3,'created/updated:', dup_file)

def get_required_data(duplicate_dict):
    ''' The duplicate information returned above is a little sparse (obs80-only)
        Let's get all of the required data in a nice format ...
    '''
    out_dict = {}
    for i, obs80bit in enumerate(list(duplicate_dict.keys())):
        filepath_lst = duplicate_dict[obs80bit]
        
        out_dict[obs80bit] = []
        for j,filepath in enumerate(filepath_lst):
            # Grep in the original file for the obs80 bit
            command = f'grep "{obs80bit}" {filepath}'
            process = subprocess.Popen( command,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        shell=True
            )
            stdout, stderr = process.communicate()
            stdout = stdout.decode("utf-8").split('\n')[0]
 
            out_dict[obs80bit].append(f"{i},{j},{stdout}:{filepath}")
    return out_dict

def fix_cross_desig_duplicates():#dup_file_list):

    # Make a list of filenames to loop through
    dup_file_list = []
    for i in range(12):
        for j in range(i+1,12):
            dup_file_list.append( 'cross_des_duplicates_{i}_{j}.txt' )
            
    # Loop through the files ...
    for fp in dup_file_list:
        # read ...
        with open(fp,'r') as fh:
            data = fh.readlines()
        # parse ...
        for l, line in enumerate(data):
            i,j,stdout,filepath = line.split(",")
        

if __name__ == '__main__':
    dup_file_list , duplicates = find_cross_desig_duplicates()
    #fix_cross_desig_duplicates(duplicates)
