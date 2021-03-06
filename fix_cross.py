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
#from joblib import Parallel, delayed

# Functions to *FIND*  cross-desig duplicates ...
#----------------------------------------------------
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
    #files_.extend( [_ for _ in glob.glob(f'/sa/obs/*num', recursive=True) if _ not in filenames_to_ignore] )

    return files_
    
def _get_unnumbered_filenames(  ):
    ''' get filenames for unnumbered observations (primary data files)'''

    filenames_to_ignore = []

    # ---------------- UN-numbered FILES -----------
    files_ = []
    files_.extend( [_ for _ in glob.glob(f'/sa/mpu/U*dat', recursive=True) if _ not in filenames_to_ignore] )
    #files_.extend( [_ for _ in glob.glob(f'/sa/obs/*unn', recursive=True) if _ not in filenames_to_ignore] )

    return files_


def split_into_groups(filepath_list, group_size = 30 ):
    ''' Split files into "groups" of filenames'''
    group_dict = {}
    for i, filepath in enumerate(filepath_list):
        grp_num = 'Grp' + str(i // group_size)
        
        if grp_num not in group_dict:
            group_dict[grp_num] = []
            
        group_dict[grp_num].append(filepath)
    
    print(f"split_into_groups: N_groups = {len(group_dict)}, N_files = {len(filepath_list)}")
    print(f"\t expect ~ {len(group_dict)}^2/2 ~ {(len(group_dict)**2)/2} sets of runs ...")
    return group_dict

def load_grp_obs(filepath_list):
    ''' load the contents of all files into a dict '''
    obs_dict = {}
    print('...loading...')
    for i, fp in enumerate(filepath_list):
        print('.', end='', flush=True )
        # Read the file contents into a dictionary
        with open(fp,'r') as fh:
            # NB: This will overwrite/ignore any duplicates that occur within the same file
            obs_dict[fp] = {line[15:56]:fp for line in fh if line[14] not in ['s','v']}
    print()
    return obs_dict

def intersecn_func(d1,d2):
    DUP = defaultdict(list)

    # intersecn indicates duplicate obs80-bits
    intersecn = d1.keys() & d2.keys()
    print('.', end='', flush=True )

    # store duplicates with list of file-paths
    for k in intersecn:
        DUP[k].append(d1[k])
        DUP[k].append(d2[k])
    
    return DUP

def find_duplicates(obs_dict):
    
    # We will read all data into a single big dictionary
    ALL = {}
    DUP = defaultdict(list)
    
    # Loop through all of the dictionaries that have been loaded
    print('...finding duplicates...')
    fps = list(obs_dict.keys())
    
    for i in range(len(fps)):
        print('\t', f'{i}/{len(fps)}' , end=', ', flush=True )
        for j in range(i+1,len(fps)):
            print('.', end='', flush=True )
            fp1, fp2 = fps[i], fps[j]
            
            
            # intersecn indicates duplicate obs80-bits
            intersecn = obs_dict[fp1].keys() & obs_dict[fp2].keys()

            # store duplicates with list of file-paths
            for k in intersecn:
                DUP[k].append(obs_dict[fp1][k])
                DUP[k].append(obs_dict[fp2][k])
            
            
        print()
    
    

    del ALL
    return DUP

def find_cross_desig_duplicates(save_dir) :
    duplicates = {}
    dup_file_list = []
    
    # Get all filenames of "primary" data files
    filepath_list = sorted(_get_filenames())

    
    # Split files into "groups" of filenames
    group_dict = split_into_groups(filepath_list)
    
    # Loop over Groups
    grp_names = list(group_dict.keys())
    for i in range(len(grp_names)):
        for j in range(i+1,len(grp_names)):
            ''' There is some kind of problem / stall with grp_i,grp_j=0,11'''
            grp_i,grp_j = grp_names[i], grp_names[j]
            
            print('\n',grp_i,grp_j)

            # load the contents of all files in each grp into a dict
            obs_dict_grp = load_grp_obs( group_dict[grp_i] )
            obs_dict_grp.update( load_grp_obs( group_dict[grp_j] ) )
            print("N_loaded = ", len(obs_dict_grp) )
            
            # I don't think we need to bother finding duplicates within an individual group
            # Instead just find any duplicates anywhere across the loaded contents
            duplicated_obs80_dict = find_duplicates(obs_dict_grp)
            
            # The duplicate information returned above is a little sparse (obs80-only)
            # - Let's get all of the required data in a nice format ...
            duplicates = get_required_data(duplicated_obs80_dict)

            # Record the duplicates
            dup_file_list.append( save_duplicates(i,j, duplicates , save_dir) )
            
        
    return True
        
def save_duplicates(i,j, duplicate_dict, save_dir):
    print('save_duplicates:', i,j, len(duplicate_dict))
    dup_file = os.path.join(save_dir , f'cross_des_duplicates_{i}_{j}.txt')
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
        print('get_required_data...')
        print(i, obs80bit)
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
            print(command)
            print(stdout)
            print()
            out_dict[obs80bit].append(f"{i},{j},{stdout},{filepath}")
    return out_dict





# Functions to *FIX*  cross-desig duplicates ...
#----------------------------------------------------
def fix_cross_desig_duplicates(save_dir):
    ''' fix_cross_desig_duplicates that were previously identified using find_cross_desig_duplicates '''
    discard, keep, notfixed = [],[],[]

    # Make a list of filenames to loop through
    dup_file_list = glob.glob( save_dir + '/cross_des_duplicates*')

    # Loop through the files ...
    print('Attempting to fix ...' )
    for fp in dup_file_list:
        print(fp)
        # read ...
        with open(fp,'r') as fh:
            data = fh.readlines()
            
        # parse ...
        '''
        0,0,c4896K01DB2A* C2001 02 19.09477 07 59 11.94 +21 23 48.6 K08W35H  21.8 Vd@6513691:/sa/mpn/N0384001.dat
        0,1,Y6603K08W35H  C2001 02 19.09477 07 59 11.94 +21 23 48.6          21.8 Vd~034c691:/sa/mpn/N0346001.dat
        1,0,c4896K01DB2A  C2001 02 19.11899 07 59 11.02 +21 23 50.2 K08W35H  22.0 Vd@6513691:/sa/mpn/N0384001.dat
        1,1,Y6603K08W35H  C2001 02 19.11899 07 59 11.02 +21 23 50.2          22.0 Vd~034c691:/sa/mpn/N0346001.dat
        2,0,c4896K01DB2A  C2001 02 19.14238 07 59 10.07 +21 23 51.3 K08W35H  22.2 Vd@6513691:/sa/mpn/N0384001.dat
        2,1,Y6603K08W35H  C2001 02 19.14238 07 59 10.07 +21 23 51.3          22.2 Vd~034c691:/sa/mpn/N0346001.dat
        '''
        issue_dict = {}
        for l, line in enumerate(data):

            dup_num = line.split(",")[0]
            if dup_num not in issue_dict: issue_dict[dup_num] = []
            issue_dict[ dup_num ].append( line )
        
        # fix
        for k, line_list in issue_dict.items():
        
            d, k, n = decide_how_to_fix(line_list)
            
            discard.extend(d)
            keep.extend(k)
            notfixed.extend(n)
            
    # print/write
    write_attempted_fixes(discard, keep, notfixed , save_dir)
        
            
def decide_how_to_fix(line_list):
    ''' fix a list of duplicates (where possible) '''

    if len( [ _ for _ in line_list if "/sa/mpu/u" in _] ):
        # This is a lowercase file: ignore
        # *** MJP:2021-05-11: I don't remember why I wanted to ignore lower-case filenames ... typo?duplicates?temporary?...***
        discard, keep, notfixed = [],[],[]
        
    elif len(line_list) == 2:
        line1, line2 = line_list[0], line_list[1]
        obs1, obs2   = line1.split(",")[2], line2.split(",")[2]
        f1, f2       = line1.split(",")[3], line2.split(",")[3]
        prov1,prov2  = obs1[5:12].strip(),obs2[5:12].strip()
        ast1,ast2    = obs1[12],obs2[12]
        N2_1,N2_2    = obs1[14],obs2[14]

        # If we have the case where there is an asterisk & a "X" in one of the pair, then keep both
        # - This is the stupid case where we are not really keeping it with the object, but we are for the sake of discovery.
        # - Are something stupid like that.
        if (ast1=='*' and N2_1.upper()=='X' and ast2!='*' and N2_1.upper()!='X') or (ast1!='*' and N2_1.upper()!='X' and ast2=='*' and N2_1.upper()=='X'):
            discard, keep, notfixed = [], line_list, []

        # if one of the provIDs is in the later part of the other, that implies a redesignation
        elif prov1 != '' and prov1 in obs2[50:]:
            discard, keep, notfixed = [f'{obs1},{f1}'], [f'{obs2},{f2}'], []
        elif prov2 != '' and prov2 in obs1[50:]:
            discard, keep, notfixed = [f'{obs2},{f2}'], [f'{obs1},{f1}'], []
            
        # if we get to here, then we don;'t know how to fix ...
        else:
            discard, keep, notfixed = [],[],line_list

    else:
        discard, keep, notfixed = [],[],line_list
        
    return discard, keep, notfixed

def write_attempted_fixes(discard, keep, notfixed , save_dir):
    ''' write out the results of our attempt fix'''
    
    # Lines that we want to delete/discard
    discard_file = os.path.join(save_dir , 'to_be_deleted.txt')
    print(f'There are {len(list(set(discard)))} observations in {discard_file} to be deleted')
    with open(discard_file, 'w') as fh:
        for line in list(set(discard)):
            fh.write( line + '' if line[-1]=='\n' else '\n')
            
    # Lines that we don't know how to fix
    not_fixed = os.path.join(save_dir , 'not_fixed.txt')
    uniq_not_fixed = []
    for line in notfixed:
        if line not in uniq_not_fixed:
            uniq_not_fixed.append(line)
    print(f'There are {len(uniq_not_fixed)} observations in {not_fixed} that I do not know how to fix')
    with open(not_fixed, 'w') as fh:
        for line in uniq_not_fixed:
            fh.write( line + '' if line[-1]=='\n' else '\n')


# command-line running ...
#----------------------------------------------------
if __name__ == '__main__':
    save_dir = os.getcwd() if len(sys.argv) == 1 else sys.argv[1]
    find_cross_desig_duplicates( save_dir )
    fix_cross_desig_duplicates(  save_dir )
