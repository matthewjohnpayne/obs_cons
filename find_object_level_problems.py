'''
Code to find problems at the object level
E.g.: No asterisk
 Does not fix
'''

# third party imports
#-----------------------
import sys, os
import glob


# Functions to *FIND*  individual problems ...
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


def _asterisk_exists(deduped_obs_list):
    '''
    # Missing asterisk
    '''
    
    asterisk = False
    
    for obs80str in deduped_obs_list:
        # look for an asterisk in position [12]
        if obs80str[12] == "*":
            asterisk = True
            break
        
            
    return asterisk


def save_problems_to_file(save_dir , outfilename , desig_list, filepath):
    '''
    '''
    with open( os.path.join(save_dir , outfilename) , 'w') as fh:
        print('\t', os.path.join(save_dir , outfilename))
        for desig in desig_list:
            fh.write(f'{desig}, {filepath}\n')
            
    
def find_object_level_problems_in_one_file(filepath , save_dir):
    print(filepath)
    filename = filepath.split("/")[-1]
    
    # read the data
    with open(filepath,'r') as fh:
        obs = fh.readlines()
        
    # split by object
    object_obs_dict = {}
    for l,line in enumerate(obs):
        
        # extract designation
        desig = line[:5] if filename[0] == "N" else line[5:12]
        desig = desig.strip()
        assert len(desig) > 3
        
        # ensure there is a list to append to
        if desig not in object_obs_dict:
            object_obs_dict[desig]=[]
        
        # append obs
        object_obs_dict[desig].append(line)
        
    # Loop and fix ...
    missing_asterisk = []
    for desig, obs_list in object_obs_dict.items():
    
        # (1) Missing asterisk
        if not _asterisk_exists(obs_list):
            missing_asterisk.append(desig)
    
        # (2)  ... other problems we come across ...
    
    # write out the problems
    for outfilename, desig_list in zip(
                    ['missing_asterisk'],
                    [missing_asterisk]
                    ):
        save_problems_to_file(save_dir , outfilename , desig_list, filepath)


def find_all(save_dir):
    
    # Get all filenames of "primary" data files
    filepath_list = sorted(_get_filenames())

    # Process each file
    # *** LIMITED TO ONE FILE WHILE DEVELOPING ***
    for filepath in filepath_list[:2]:
    
        # find the problems
        find_object_level_problems_in_one_file(filepath , save_dir)
        
        # add code to fix problems
        

if __name__ == '__main__':
    
    save_dir = os.getcwd() if len(sys.argv) == 1 else sys.argv[1]
    find_all(save_dir)
