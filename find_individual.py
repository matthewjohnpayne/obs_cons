'''
Code to find problems with *individual* lines in obs80 files
 - Not duplicates
 
Does not fix, just prints the problems out to file

MJP 2021-03-19

'''

# third party imports
#-----------------------
import sys, os
import glob
import math

# local imports
# -----------------
sys.path.insert(0,'/share/apps/obs80/')
import obs80

# Read all current obcCodes ...
with open('/sa/data/obscode.dat', 'r') as fh:
    obsCodeDict = {_[:4].strip():True for _ in fh.readlines() }

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
        if len(pub_ref.strip()) != 5 :
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
        # the notes are in posn 15 (python 14) of the obs80 string
        # they are not supposed to be blank: P   Photographic (default if column is blank)
        # https://www.minorplanetcenter.net/iau/info/OpticalObs.html
        pub_ref = obs80str[14]
        
        # the single character should NOT be white space.
        if len(pub_ref.strip()) != 1 :
            pub_ref_problems.append(obs80str)
            
    return pub_ref_problems

def _check_o80parse(deduped_obs_list):
    '''
    # Will Sonia's obs80 code parse it?
    '''
    
    # list to hold any problematic observations
    parse_problems = []
    
    for obs80str in deduped_obs_list:
        try:
            # ignore sat/rov/radar lines
            if obs80str[14] in 'srvSRV':
                pass
            else:
                obs80.parseOpt(obs80str)
        except:
            parse_problems.append( obs80str )
            
    return parse_problems

def _check_obscode(obs):
    ''' Look for obvious problems with obscodes
    E.g. obscodes that dont exist or are not allowed
    '''
    # list to hold any problematic observations
    obscode_problems = []
    
    for obs80str in obs:
        if obs80str[14] not in ['s','v','r']:
            obsCode = obs80str[77:80]
        
            if obsCode in ['XXX','   ','310'] or obsCode not in obsCodeDict:
                obscode_problems.append(obs80str)
            
    return obscode_problems


def _check_datetime(obs):
    ''' Look for obvious problems with datetime
    E.g. days that are > than the number of days in the month
    '''
    # list to hold any problematic observations
    datetime_problems = []
    
    for obs80str in obs:
        if obs80str[14] not in ['s','v','r']:
            dt = obs80str[15:32]
            
            yr = dt[0:4]
            mn = dt[5:7]
            frac, dy = math.modf(float(dt[8:]))
            
            try:
                # Check the year is reasonable
                assert int(yr) <= 2021

                # Check the month is reasonable
                assert int(mn) >= 1 and int(mn) <= 12
                
                # Check the day is reasonable
                if int(mn) == 2 :
                    assert int(dy) < 30
                elif int(mn) in [9,4,6,11]:
                    assert int(dy) < 31
                else:
                    assert int(dy) < 32

            except:
                datetime_problems.append(obs80str)
            

    return datetime_problems

def _check_radec(obs):
    ''' Look for obvious problems with ra/dec
    E.g. mins/secs that are > 60 
    '''

    # list to hold any problematic observations
    radec_problems = []
    
    for obs80str in obs:
        if obs80str[14] not in ['s','v','r']:
            try:
                # extract ra, dec strings
                ra, dec = obs80str[32:44], obs80str[44:56]
                
                # get ra, dec floats
                ra_hr   = float(ra[0:2])
                dec_deg = float(dec[1:3])
                
                ra_mn = float(ra[3:5])
                try:
                    ra_sec = float(ra[6:])
                except ValueError:
                    ra_sec = 0

                dec_mn = float(dec[4:6])
                try:
                    dec_sec = float(dec[7:])
                except ValueError:
                    dec_sec = 0

                # check values ...
                assert ra_hr < 24.0
                assert dec_deg > -90. and dec_deg < 90.
                
                assert ra_mn   < 60.0
                assert ra_sec  < 60.0
                assert dec_mn  < 60.0
                assert dec_sec < 60.0
            except:
                radec_problems.append(obs80str)
            
    return radec_problems
    
def save_problems_to_file(save_dir , outfilename , obs_list , filepath):
    '''
    Print problems to file so that they can be examined and fixed later
    '''
    with open( os.path.join(save_dir , 'individual_'+outfilename) , 'a') as fh:
        print('\t', os.path.join(save_dir , outfilename))
        for obs in obs_list:
            o = obs[:-1] if obs[-1] == '\n' else obs
            fh.write(f'{o}:{filepath}\n')
            
    
def find_individual_problems_in_one_file(filepath , save_dir):
    '''
    Examine a primary data file for all of the 'individual line' problems that I can think of
    '''
    print(filepath)
    
    # read the data
    with open(filepath,'r') as fh:
        obs = fh.readlines()
        
    # (1) Missing pubn references
    missing_pub_ref = _check_refs(obs)
    
    # (2) Missing notes
    # Sometimes we do not have "Note 2" before 2020 in obs80: replace blank with default ?
    missing_notes = _check_notes(obs)
        
    # (3) bad obscodes (XXX, ...)
    obscode_problems = _check_obscode(obs)

    # (4) incorrect dates/times (min >= 60, dates >= 32, wtc)
    datetime_problems = _check_datetime(obs)

    # (5) Will not parse using Sonia's obs80 code
    radec_problems = _check_radec(obs)

    # (6) Will not parse using Sonia's obs80 code
    parse_problems = _check_o80parse(obs)

    # ... other problems we come across ...
    
    # write out the problems
    for outfilename, obs_list in zip(
                    ['missing_pub_ref','missing_notes','parse_problems', 'obscode_problems', 'datetime_problems','radec_problems'],
                    [missing_pub_ref,   missing_notes,  parse_problems,   obscode_problems,   datetime_problems , radec_problems]
                    ):
        save_problems_to_file(save_dir , outfilename , obs_list , filepath)


def find_all(save_dir):
    
    # Get all filenames of "primary" data files
    filepath_list = sorted(_get_filenames())

    # Process each file
    # *** LIMITED TO ONE FILE WHILE DEVELOPING ***
    for filepath in filepath_list[:22]:
    
        # find the problems
        find_individual_problems_in_one_file(filepath , save_dir)
        
        # add code to fix problems
        

if __name__ == '__main__':
    
    save_dir = os.getcwd() if len(sys.argv) == 1 else sys.argv[1]
    find_all(save_dir)
