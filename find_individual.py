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

# obs-codes that are allowed 2-lines
allowed_2line = { _ : True for _ in ['244', '245', '247','248','249', '250', '258', '500', 'C49','C50','C51','C52','C53','C54','C55', 'C56', 'C57', '251', '252', '253', '254', '255', '256' , '257' ] }

# Functions to *FIND*  individual problems ...
#----------------------------------------------------
def _get_filenames():
    ''' get a dict containing all the filenames we want to work with ...'''
    
    # Get filenames for num & unnum observations
    files_ = _get_numbered_filenames()
    #files_.extend(_get_unnumbered_filenames())
    
    return files_
    
def _get_numbered_filenames():
    ''' get filenames for numbered observations (primary data files)'''

    filenames_to_ignore = ['unpub.num']

    # ------------ NUMBERED FILES ------------------
    # Primary, published files
    files_ = [_ for _ in glob.glob(f'/sa/mpn/N0000011*dat', recursive=True) if _ not in filenames_to_ignore]
    print("files_=", files_)
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


def _check_refs( obs80str):
    '''
    # Missing pubn references
    '''
    
    # the pub-ref is in posns 72:77 of the obs80 string
    pub_ref = obs80str[72:77]
    
    # there should be 5 non-white space characters. If not, flag as a problem
    # - perhaps this logic will turn out to be wrong for ancient pubns.
    # C'est la vie
    return [obs80str] if len(pub_ref.strip()) != 5 else []

def _check_notes(obs80str):
    '''
    # Missing notes
    # Sometimes we do not have "Note 2" before 2020 in obs80: replace blank with default ?
    '''
    
    # the notes are in posn 15 (python 14) of the obs80 string
    # they are not supposed to be blank: P   Photographic (default if column is blank)
    # https://www.minorplanetcenter.net/iau/info/OpticalObs.html
    pub_ref = obs80str[14]
    
    # the single character should NOT be white space.
    return [obs80str] if len(pub_ref.strip()) != 1 else []

def _check_obscode(obs80str):
    ''' Look for obvious problems with obscodes
    E.g. obscodes that dont exist or are not allowed
    '''
    obsCode = obs80str[77:80]
    return [obs80str] if ( obsCode in ['XXX','   ','310'] or obsCode not in obsCodeDict ) else []
        

def _check_datetime(obs80str):
    ''' Look for obvious problems with datetime
    E.g. days that are > than the number of days in the month
    '''
    # Boolean for pass/fail
    SUCCESS = True

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
            
            # Boolean
            SUCCESS = True
        except:
            SUCCESS = False

    
    return [obs80str] if not SUCCESS else []
    


def _check_radec(obs80str):
    ''' Look for obvious problems with ra/dec
    E.g. mins/secs that are > 60 
    '''
    # Boolean for pass/fail
    SUCCESS = True
    if obs80str[14] not in ['s','v','r','R']:
        try:
            # extract ra, dec strings
            ra_hr, dec_deg = obs80.RA2hrRA(obs80str[32:44]), obs80.Dec2degDec(obs80str[44:56])
            
            # check values ...
            assert ra_hr < 24.0
            assert dec_deg > -90. and dec_deg < 90.
            
            SUCCESS = True
        except Exception as e:
            SUCCESS = False
            
            print('Exception = ',e)
            print(obs80str)
 
    return [obs80str] if not SUCCESS else []

def _check_2line( line1, line2 ):
    ''' check that both lines in a two line observation are present
    #
    #E4950         S2019 05 03.21923614 18 31.29 -25 36 11.4          19.4 GV~3cC3C57
    #E4950         s2019 05 03.2192361 -195500.638 +261270.092 -58409.1580   ~3cC3C57
    #
    '''
    # If we are dealing with the first line in a pair, we expect upper case ...
    # ... don't worry about checking second lines alone ...
    return [line1] if line1[14] in 'SRV' and line2[14] not in 'srv' else []

def _check_ineligible_2line( obs80str ):
    ''' Look for Two line observations against obs_code that is not allowed to have 2-line observations s'''

    # Look for sat/rov/radar lines
    # We expect the sat/rov/radar obs to come from the above list
    # If obs-code not in allowed list, then treat as problem
    return [obs80str] if obs80str[14] in 'srvSRV' and obs80str[77:80] not in allowed_2line else []


def _check_o80parse(obs80str):
    '''
    # Will Sonia's obs80 code parse it?
    '''
    
    try:
        # ignore sat/rov/radar lines
        if obs80str[14] in 'srvSRV':
            pass
        else:
            obs80.parseOpt(obs80str)
        return []
    except:
        return [obs80str]


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
    
    # Name of file & associated list we'll use to store problems
    files_and_lists = { _:[] for _ in [ 'missing_2line',
                                        'missing_pub_ref',
                                        'missing_notes',
                                        'parse_problems',
                                        'obscode_problems',
                                        'datetime_problems',
                                        'radec_problems',
                                        'ineligible_2line'] }

    # Open file
    # Do stream processing to allow for large files
    # For each line in file, check for problems
    prev_line = None
    with open(filepath,'r') as fh:
        for line in fh:
        
            # (0) Check 2-line obs for missing 2nd line
            if prev_line is not None:
                files_and_lists['missing_2line'].extend( _check_2line( prev_line, line ) )

            # (1) Missing pubn references
            files_and_lists['missing_pub_ref'].extend( _check_refs( line ) )
            
            # (2) Missing notes
            # Sometimes we do not have "Note 2" before 2020 in obs80: replace blank with default ?
            files_and_lists['missing_notes'].extend( _check_notes( line ) )
                
            # (3) bad obscodes (XXX, ...)
            files_and_lists['obscode_problems'].extend( _check_obscode( line ) )

            # (4) incorrect dates/times (min >= 60, dates >= 32, wtc)
            files_and_lists['datetime_problems'].extend( _check_datetime( line ) )

            # (5) Some kind of problem with the ra/dec values
            files_and_lists['radec_problems'].extend( _check_radec( line ) )

            # (6) Two line observations against wrong obs_code
            files_and_lists['ineligible_2line'].extend( _check_ineligible_2line( line ) )

            # (7) Will not parse using Sonia's obs80 code
            files_and_lists['parse_problems'].extend( _check_o80parse( line ) )
    
            # ... other problems we come across ...
    
    # write out the problems
    for outfilename in files_and_lists:
        save_problems_to_file(save_dir , outfilename , files_and_lists[outfilename] , filepath)


def find_all(save_dir):
    
    # Get all filenames of "primary" data files
    filepath_list = sorted(_get_filenames())

    # Process each file
    for filepath in filepath_list:
    
        # find the problems
        find_individual_problems_in_one_file(filepath , save_dir)
        
        # add code to fix problems
        

if __name__ == '__main__':
    
    save_dir = os.getcwd() if len(sys.argv) == 1 else sys.argv[1]
    find_all(save_dir)
