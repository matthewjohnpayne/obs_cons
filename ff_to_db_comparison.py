'''
Code to compare ff observations to db observatitons

Going to make the strong assumption that the flat-files are to be prefered / believed where possible (obvious exceptions are when an observation exists in the db but not in any ff)

NB Going to point out here ...
 - We need to understand whether there are observations in the database that are not in the flat-files: if so, what do we need to do with them?
'''

# third party imports
#-----------------------
import sys, os
import glob


# Functions to *FIND* find files ...
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
    files_.extend( [_ for _ in glob.glob(f'/sa/obs/*num', recursive=True) if _ not in filenames_to_ignore] )

    return files_
    
def _get_unnumbered_filenames(  ):
    ''' get filenames for unnumbered observations (primary data files)'''

    filenames_to_ignore = []

    # ---------------- UN-numbered FILES -----------
    files_ = []
    files_.extend( [_ for _ in glob.glob(f'/sa/mpu/U*dat', recursive=True) if _ not in filenames_to_ignore] )
    files_.extend( [_ for _ in glob.glob(f'/sa/obs/*unn', recursive=True) if _ not in filenames_to_ignore] )

    return files_


def compare_ff_and_db_for_single_desig( desig , NUMBERED):
    '''
    Compare the observational data for a single designation
    Flat-Files 'vs' Database
    '''
    
    # Get the flat-file data
    flat_file_data = get_ff(desig, NUMBERED )
    
    # Get the database data
    
    # Compare the data
    
    

def loop_through_designations( METHOD = 'PRIMARY' ):
    '''
    Iterate over all possible designations
    More than one way to do this ...
    (1) All primary desigs in current_designations
    (2) All desigs of any kind in current_designations
    (3) All desigs in the "primary data files"
    ...
    Probably best to try them all at some point ...
    '''

    # Get the list of designations to be searched ...
    if   METHOD == "PRIMARY":
        # get the primary designations from the current identifications table
        # NB it will be convenient to have them split into numbered and unnumbered
        pass
    elif METHOD == "SECONDARY":
        pass
    elif METHOD == "DATA":
        pass
    else:
        pass
    
    # Loop through the designations ...
    for num_desig in numbered_designations:
        compare_ff_and_db_for_single_desig(num_desig , True)
    for unn_desig in unnumbered_designations:
        compare_ff_and_db_for_single_desig(unn_desig , False)

if __name__ == '__main__':
    
    save_dir = os.getcwd() if len(sys.argv) == 1 else sys.argv[1]
    
