'''
Code to find problems with *individual* lines
 - Not duplicates
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
    files_.extend( [_ for _ in glob.glob(f'/sa/mpu/*dat', recursive=True) if _ not in filenames_to_ignore] )
    #files_.extend( [_ for _ in glob.glob(f'/sa/obs/*unn', recursive=True) if _ not in filenames_to_ignore] )

    return files_


def _check_refs(deduped_obs_list):
    '''
    # Missing pubn references
    '''
    
    # list to hold any problematic observations
    pub_ref_problems = []
    
    for obs80str in deduped_obs_list:
        # the pub-ref is in posns 72:77 of the obs80 string
        pub_ref = obs80str[72:77]
        
        # there should be 5 non-white space characters. If not, flag as a problem
        # - perhaps this logic will turn out to be wrong for ancient pubns.
        # C'est la vie
        if len(pub_ref.strip) != 5 :
            pub_ref_problems.append(obs80str)
            
    return pub_ref_problems

def _check_notes(deduped_obs_list):
    '''
    # Missing notes
    # Sometimes we do not have "Note 2" before 2020 in obs80: replace blank with default ?
    '''
    
    # list to hold any problematic observations
    pub_ref_problems = []
    
    for obs80str in deduped_obs_list:
        # the notes are in posn ??:?? of the obs80 string
        pub_ref = obs80str[72:77]
        
        # the single character should NOT be white space.
        if len(pub_ref.strip) != 1 :
            pub_ref_problems.append(obs80str)
            
    return pub_ref_problems

def find_individual_problems_in_one_file(filepath , save_dir):
    
    # read the data
    with open(filepath,'r') as fh:
        obs = fh.readlines()
        
    # (1) Missing pubn references
    missing_pub_ref = _check_refs()
    
    # (2) Missing notes
    # Sometimes we do not have "Note 2" before 2020 in obs80: replace blank with default ?
    missing_notes = _check_notes()
    
    # (3) ... other problems we come across ...
    
    # write out the problems
    for filename, obslist in zip(
                    ['missing_pub_ref','missing_notes'],
                    [missing_pub_ref, missing_notes]
                    ):
        save_problems_to_file(save_dir , filename , obs_list)


def find_all(save_dir):
    
    # Get all filenames of "primary" data files
    filepath_list = sorted(_get_filenames())

    # Process each file
    # *** LIMITED TO ONE FILE WHILE DEVELOPING ***
    for filepath in filepath_list[:1]:
    
        # find the problems
        find_individual_problems_in_one_file(filepath , save_dir)
        
        # add code to fix problems
        

if __name__ == '__main__':
    
    save_dir = os.getcwd() if len(sys.argv) == 1 else sys.argv[1]
    find_all(save_dir)
