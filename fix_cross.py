'''
Code to look-for & fix, cross-file duplicates
I.e. observations which appear in multiple files under multiple designations

*** Do NOT run in the same way as the fix_desig / fix_prog routines ***

'''

# Third party imports
import sys, os
import glob
from collections import Mapping, Container, Counter, defaultdict

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


def split_into_groups(filepath_list, group_size = 10 ):
    ''' Split files into "groups" of filenames'''
    group_dict = {}
    for i, filepath in enumerate(filepath_list):
        grp_num = str(i // group_size)
        
        if grp_num not in group_dict:
            group_dict[grp_num] = []
            
        group_dict[grp_num].append(filepath)
    
    print(f"split_into_groups: N_groups = {len(group_dict)}, N_files = {len(filepath_list)}")
    return group_dict

def load_grp_obs(filepath_list):
    ''' load the contents of all files into a dict '''
    obs_dict = {}
    for fp in filepath_list:
        # Read the file contents into a dictionary
        with open(f,'r') as fh:
            # NB: This will overwrite/ignore any duplicates that occur within the same file
            obs_dict[fp] = {line[15:56]:True for line in fh if line[14] not in ['s','v']}
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
            DUP[k].append(local[k])
            if isinstance(ALL[k], int):
                DUP[k].append(ALL[k])
            else:
                DUP[k].extend(ALL[k])
                
        # update the overall dictionary with local data
        ALL.update(local)
        
        # update the overall dictionary with the duplicates
        ALL.update(DUP)
        print(f'\t N_All= {len(ALL)}, N_Dup= {len(DUP)}')
        
    del ALL
    return DUP

def find_cross_desig_duplicates() :
    duplicates = {}
    
    # Get all filenames of "primary" data files
    filepath_list = _get_filenames()
    
    # Split files into "groups" of filenames
    group_dict = split_into_groups(filepath_list)
    
    # Loop over Groups
    grp_names = list(group_dict.items())
    for i, grp_i in enumerate( grp_names ):
        for j, grp_j in enumerate( grp_names[i+1:] ):
            print(i,j,' ... loading...')
            
            # load the contents of all files in each grp into a dict
            obs_dict_grp_i = load_grp_obs( group_dict[grp_i] )
            obs_dict_grp_j = load_grp_obs( group_dict[grp_j] )
            
            # I don't think we need to bother finding duplicates within an individual group
            # Instead just find any duplicates anywhere across the loaded contents
            obs_dict_grp_i.update(obs_dict_grp_j)
            duplicates[(i,j)] = find_intra_group_duplicates(obs_dict_grp_i)
            
            # Record the duplicates
            save_duplicates(i,j, duplicates[(i,j)])
            
    return duplicates
        
def save_duplicates(i,j, duplicate_dict):
    print('save_duplicates:', i,j, len(duplicates))
    dup_file = os.path.join(self.save_dir , f'cross_des_duplicates_{i}_{j}.txt')
    with open( dup_file , 'w') as fh:
        for obs80bit, lst in duplicate_dict.items():
            for i,n in enumerate(lst):
                fh.write(f'{obs80bit},{i},{n}\n')
    print('\t'*3,'created/updated:', dup_file)
    sys.exit()
    
if __name__ == '__main__':
    duplicates = find_cross_desig_duplicates()
    #fix_cross_desig_duplicates(duplicates)
