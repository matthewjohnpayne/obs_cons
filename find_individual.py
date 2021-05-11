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

# allowed Ast-Cat values
with open ('/sa/god_fit/lib/catalogue.txt' , 'r') as fh:
    allowed_AstCat = { _[:5].strip() : True for _ in fh.readlines() }
print('allowed_AstCat' , allowed_AstCat)

# allowed Mag0-Band values
# (1) Copied from here: https://www.minorplanetcenter.net/iau/info/OpticalObs.html
# 'B', 'V', 'R','I', 'J','W', 'U', 'g', 'r', 'i', 'w', 'y', 'z'
# Almost certainly INCOMPLETE!!!
#
# (2) Found in xmlto80.py
# new_style_bands = ['Vj', 'Rc', 'Ic', 'Bj', 'Uj', 'Sg', 'Sr', 'Si', 'Sz', 'Pg', 'Pr', 'Pi', 'Pz', 'Pw', 'Py', 'Ao', 'Ac', 'Gb', 'Gr']
# old_style_bands = ['V', 'R', 'I', 'B', 'U', 'g', 'r', 'i', 'z', 'g', 'r', 'i', 'z', 'w', 'y', 'o', 'c', 'G', 'G']
#
# (3) From Dave...
'''
[('a', 'USNOA1'), ('b', 'USNOSA1'), ('c', 'USNOA2'),

            ('d', 'USNOSA2'), ('e', 'UCAC1'), ('f', 'Tyc1'),

            ('g', 'Tyc2'), ('h', 'GSC1.0'), ('i', 'GSC1.1'),

            ('j', 'GSC1.2'), ('k', 'GSC2.2'), ('l', 'ACT'),

            ('m', 'GSCACT'), ('n', 'SDSS8'), ('o', 'USNOB1'),

            ('p', 'PPM'), ('q', 'UCAC4'), ('r', 'UCAC2'),

            ('s', 'USNOB2'), ('t', 'PPMXL'), ('u', 'UCAC3'),

            ('v', 'NOMAD'), ('w', 'CMC14'), ('x', 'Hip2'),

            ('y', 'Hip1'), ('z', 'GSC'), ('A', 'AC'),

            ('B', 'SAO1984'), ('C', 'SAO'), ('D', 'AGK3'),

            ('E', 'FK4'), ('F', 'ACRS'), ('G', 'LickGas'),

            ('H', 'Ida93'), ('I', 'Perth70'), ('J', 'COSMOS'),

            ('K', 'Yale'), ('L', '2MASS'), ('M', 'GSC2.3'),

            ('N', 'SDSS7'), ('O', 'SSTRC1'), ('P', 'MPOSC3'),

            ('Q', 'CMC15'), ('R', 'SSTRC4'), ('S', 'URAT1'),

            ('T', 'URAT2'), ('U', 'Gaia1'), ('V', 'Gaia2'),

            ('W', 'UCAC5') ]
'''
#
# (4) From Federica
'''
W    Gaia-DR3
X    Gaia-EDR3
Y    UCAC-5
Z    ATLAS-2
'''
#
# (5) In formatobs.f90 (instructinos from MR)
formatobs_data = '''
  SELECT CASE (T12(1:K))
    CASE ("USNO-A1.0","USNO-A 1.0","USNO - A1.0","A1.0","A 1.0","A1","A 1","USNO A1","USNO A1.0","USNO A-1.0","USNO A-1","USNO-A1","USNOA1")
      T12A = "USNO-A1.0"
      T1 = "a"
    CASE ("USNO-SA1.0","USNO-SA 1.0","USNO - SA1.0","SA1.0","SA 1.0","SA1","SA 1","USNO SA1","USNO SA1.0","USNO SA-1.0","USNO SA-1","USNO-SA1","USNOSA1")
      T12A = "USNO-SA1.0"
      T1 = "b"
    CASE ("USNO-A2.0","USNO-2.0","USNO-A-2.0","USNO-A 2.0","USNO - A2.0","A2.0","A 2.0","A2","A 2","USNO A2","USNO A2.0","USNO A-2.0","USNO A-2","USNO-A2","USNOA-2.0","USNO 2.0","USNOA2")
      T12A = "USNO-A2.0"
      T1 = "c"
    CASE ("USNO-SA2.0","USNO-SA 2.0","USNO - SA2.0","SA2.0","SA 2.0","SA2","SA 2","USNO SA2","USNO SA2.0","USNO SA-2.0","USNO SA-2","USNO-SA2","USNOSA2")
      T12A = "USNO-SA2.0"
      T1 = "d"
    CASE ("UCAC1","UCAC-1","UCAC-1.0","UCAC - 1.0","UCAC 1","UCAC 1.0")
      T12A = "UCAC-1"
      T1 = "e"
    CASE ("TYCHO1","TYCHO-1","TYCHO 1","TYC 1","TYC-1","Tyc1")
      T12A = "Tycho-1"
      T1 = "f"
    CASE ("TYCHO2","TYCHO-2","TYCHO 2","TYC 2","TYC-2","Tyc2")
      T12A = "Tycho-2"
      T1 = "g"
    CASE ("GSC-1.0","GSC 1.0","GSC1.0")
      T12A = "GSC-1.0"
      T1 = "h"
    CASE ("GSC-1.1","GSC 1.1","GSC1.1")
      T12A = "GSC-1.1"
      T1 = "i"
    CASE ("GSC-1.2","GSC 1.2","GSC1.2")
      T12A = "GSC-1.2"
      T1 = "j"
    CASE ("GSC-2.2","GSC 2.2","GSC2.2")
      T12A = "GSC-2.2"
      T1 = "k"
    CASE ("ACT")
      T12A = "ACT"
      T1 = "l"
    CASE ("GSC-ACT","GSCACT")
      T12A = "GSC-ACT"
      T1 = "m"
    CASE ("SDSS-DR8","SDSS-R8","SDSS8")
      T12A = "SDSS-DR8"
      T1 = "n"
    CASE ("USNO-B1.0","USNO-B 1.0","USNO - B1.0","B1.0","B 1.0","B1","B 1","USNO B1","USNO B1.0","USNO B-1.0","USNO B-1","USNO-B1","USNOB1")
      T12A = "USNO-B1.0"
      T1 = "o"
    CASE ("PPM")
      T12A = "PPM"
      T1 = "p"
    CASE ("UCAC4","UCAC-4","UCAC-4.0","UCAC - 4.0","UCAC 4","UCAC 4.0","USNO-UCAC4")
      T12A = "UCAC-4"
      T1 = "q"
    CASE ("UCAC2","UCAC-2","UCAC-2.0","UCAC - 2.0","UCAC 2","UCAC 2.0","USNO-UCAC2")
      T12A = "UCAC-2"
      T1 = "r"
    CASE ("USNO-B2.0","USNO-B 2.0","USNO - B2.0","B2.0","B 2.0","B2","B 2","USNO B2","USNO B2.0","USNO B-2.0","USNO B-2","USNO-B2","USNOB2")
      T12A = "USNO-B2.0"
      T1 = "s"
    CASE ("PPMXL","PPM-XL")
      T12A = "PPMXL"
      T1 = "t"
    CASE ("UCAC3","UCAC-3","UCAC-3.0","UCAC - 3.0","UCAC 3","UCAC 3.0")
      T12A = "UCAC-3"
      T1 = "u"
    CASE ("NOMAD")
      T12A = "NOMAD"
      T1 = "v"
    CASE ("CMC","CMC-14")
      T12A = "CMC"
      T1 = "w"
    CASE ("HIPPARCOS 2","HIPPARCOS-2","HIP 2","HIP-2","Hip2")
      T12A = "Hip-2"
      T1 = "x"
    CASE ("HIPPARCOS","HIP","Hip1")
      T12A = "Hip"
      T1 = "y"
    CASE ("GSC")
      T12A = "GSC"
      T1 = "z"
    CASE ("AC")
      T12A = "AC"
      T1 = "A"
    CASE ("SAO 1984")
      T12A = "SAO1984"
      T1 = "B"
    CASE ("SAO")
      T12A = "SAO"
      T1 = "C"
    CASE ("AGK3")
      T12A = "AGK3"
      T1 = "D"
    CASE ("FK4")
      T12A = "FK4"
      T1 = "E"
    CASE ("ACRS")
      T12A = "ACRS"
      T1 = "F"
    CASE ("LICK GASPRA CATALOGUE")
      T12A = "LickGasCat"
      T1 = "G"
    CASE ("IDA93 CATALOGUE")
      T12A = "Ida93 Cat"
      T1 = "H"
    CASE ("PERTH 70")
      T12A = "Perth 70"
      T1 = "I"
    CASE ("COSMOS/UKST SOUTHERN SKY CATALOGUE")
      T12A = "COSMOS SSC"
      T1 = "J"
    CASE ("YALE")
      T12A = "Yale"
      T1 = "K"
    CASE ("2MASS")
      T12A = "2MASS"
      T1 = "L"
    CASE ("GSC-2.3","GSC 2.3","GSC2.3")
      T12A = "GSC-2.3"
      T1 = "M"
    CASE ("SDSS","SDSS-R7","SDSS-DR7","SDSS7")
      T12A = "SDSS"
      T1 = "N"
    CASE ("SSTRC1","SST-RC1")
      T12A = "SSTRC1"
      T1 = "O"
    CASE ("MPOSC3")
      T12A = "MPOSC3"
      T1 = "P"
    CASE ("CMC-15")
      T12A = "CMC-15"
      T1 = "Q"
    CASE ("SSTRC4","SST-RC4")
      T12A = "SSTRC4"
      T1 = "R"
    CASE ("URAT-1","URAT1")
      T12A = "URAT-1"
      T1 = "S"
    CASE ("URAT-2","URAT2")
      T12A = "URAT-2"
      T1 = "T"
    CASE ("Gaia-DR1","GAIA-DR1","Gaia DR1","GAIA DR1","GAIA1")
      T12A = "Gaia-DR1"
      T1 = "U"
    CASE ("Gaia-DR2","GAIA-DR2","Gaia DR2","GAIA DR2","GAIA2")
      T12A = "Gaia-DR2"
      T1 = "V"
    CASE DEFAULT
      T12A = " "
      T1 = " "
'''.split('\n')
# Summary: Given the above, for now I am ussing the following is the list of allowed single-character mag-band codes
# Not at all sure this is complete
# Not sure whether we check the single mag-band stuff anywhere in (e.g.) autoack/processobs
allowed_MagBand = { _ : True for _ in ['B', 'V', 'R','I', 'J','W', 'U', 'G', 'g', 'r', 'i', 'w', 'y', 'z','o','c']}
print('allowed_MagBand' , allowed_MagBand)
formatobs_data = [_.split('=')[1].strip().strip{'\"'}  for _ in formatobs_data if 'T1' in _ and 'T12' not in _ and '=' in _ and 'CASE' not in _ ]

print('formatobs_data' , formatobs_data)

sys.exit()






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

def _check_ineligible_AstCat( obs80str ):
    ''' Look for AstCat (astrometric catalog) values that are not allowed'''
    return [obs80str] if obs80str[14] in 'srvSRV' and obs80str[77:80] not in allowed_AstCat else []

def _check_ineligible_MagBand( obs80str ):
    ''' Look for MagBand (magnitude bandpass) values that are not allowed'''
    return [obs80str] if obs80str[14] in 'srvSRV' and obs80str[77:80] not in allowed_MagBand else []


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
                                        'ineligible_2line',
                                        'ineligible_AstCat',
                                        'ineligible_MagBand'] }

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
            
            # (7) Look for ineligible Ast-Cat
            files_and_lists['ineligible_AstCat'].extend( _check_ineligible_AstCat( line ) )

            # (8) Look for ineligible Mag-Band
            files_and_lists['ineligible_MagBand'].extend( _check_ineligible_MagBand( line ) )

            # (9) Will not parse using Sonia's obs80 code
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
