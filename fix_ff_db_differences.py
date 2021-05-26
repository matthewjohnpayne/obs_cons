import os, sys

def triple_line_sets(filepath):
    '''
    MJP: 2021-05-25
    Generator function to extract sets of three lines from file whose content is formatted as below:
    
    FF   00001         A1952 10 12.15604 05 10 12.90 +17 52 22.5                 BN012013
    DB P 00001         A1952 10 12.15604 05 10 12.90 +17 52 22.5                 BN460013
    DIFF                                                                           ^^^

    '''
    triple = []
    for row in open(filepath, "r"):
        triple.append(row)
        if triple[0][:2] != "FF" : triple.pop(0)
        if len(triple)==3:
            assert triple[0][:2] == "FF" and triple[1][:2] == "DB" and triple[2][:4] == "DIFF" , '...problem...'
            yield triple
            triple = []
    

def process_file(filepath):
    '''
    MJP: 2021-05-25
    Function to process a *DIFFERENCE* file
    
    Assumes that the provided filepath is a DIFFERENCE file generated by a code like:
    ~dbell/obscons/check_obscons.py
    
    The file is processed in 3-line chunks
    We analyse each set of 3-lines to understand the highlighted differences
    Depending on where the differencea are in the file, we use different functions to decide on the appropriate fix
    
    For now I have just written stub-functions to do *SOME* of the job of fixing asterisks & note-fields
     - The fix_asterisk & fix_note1 functions still need to be improved
     - Other people's fix_* functions will need to be added.
     
    Note that I am deliberately "fixing the obs80 string as I go along":
     - I.e. the functions operate sequentially on the obs80 string, so more and more changes can take place
    '''
    # File we will use to hold output
    with open('ff_db_differences_FLATFILE_FIXES.txt','w') as ff_out, open('ff_db_differences_DATABASE_FIXES.txt','w') as db_out :
    
        # Loop through three line chunks ...
        for ff_line, db_line, diff_line in triple_line_sets(filepath):
            
            # Strip off the first 5 characters of the obs80 lines
            ff_obs80 , db_obs80 = ff_line[5:].strip('\n'), db_line[5:].strip('\n')
            
            # Find the locations of the "^" characters
            diff = diff_line[5:].strip('\n')
            diff = [i for i in range(len(diff)) if diff.startswith('^', i)]

            # Use locations of the "^" characters to decide on what fixing functions to call
            # In particular, we will find the intersection of "diff" with predefined-ranges
            
            # fix asterisk ( NB @posn 12 in python notation, so we extract [12:13] )
            r1, r2 = 12, 13
            if list(set(diff) & set(range(r1,r2))):
                print(12, 'asterisk...')
                # get the strings that we want to exist at this location ...
                ff_replacement_substr , db_replacement_substr = fix_asterisk( ff_obs80[r1:r2] , db_obs80[r1:r2] )
                # ... update the strings
                ff_obs80, db_obs80 = update_strs(ff_obs80, db_obs80, ff_replacement_substr , db_replacement_substr, r1, r2)
                
            # fix note1 ( NB @posn 13 in python notation, so we extract [13:14] )
            r1, r2 = 13, 14
            if list(set(diff) & set(range(r1,r2))):
                # get the strings that we want to exist at this location ...
                ff_replacement_substr , db_replacement_substr    = fix_note1( ff_obs80[r1:r2] , db_obs80[r1:r2] )
                # ... update the strings
                ff_obs80, db_obs80 = update_strs(ff_obs80, db_obs80, ff_replacement_substr , db_replacement_substr, r1, r2)

            '''
            *** OTHER PEOPLE'S CODE TO BE DROPPED IN HERE ***
            
            E.g.
            # fix references
            r1, r2 = 72, 77
            if list(set(diff) & set(range(r1,r2))):
                # get the strings that we want to exist at this location ...
                ff_replacement_substr , db_replacement_substr    = fix_reference( ff_obs80[r1:r2] , db_obs80[r1:r2] )
                # ... update the strings
                ff_obs80, db_obs80 = update_strs(ff_obs80, db_obs80, ff_replacement_substr , db_replacement_substr, r1, r2)
            '''
            
            # after all fixes have been done to the strings ...
            # (1) Print to screen if ANY changes have been made to EITHER ff or db strings
            if ff_obs80 != ff_line[5:].strip('\n') or db_obs80 != db_line[5:].strip('\n'):
                print('\n','-'*33,BEFORE')
                print(ff_line[5:].strip('\n'))
                print(db_line[5:].strip('\n'))
                print(diff_line[5:].strip('\n'))
                FLAG = 'FIXED' if ff_obs80 == db_obs80 else 'NOT (COMPLETELY) FIXED'
                print('AFTER')
                print(ff_obs80, FLAG)
                print(db_obs80, FLAG)
            # (2) Write to file if EVERYTHING is fixed...
            if ff_obs80 == db_obs80:
                if ff_obs80 != ff_line[5:].strip('\n'):
                    ff_out.write(ff_obs80)
                if db_obs80 != db_line[5:].strip('\n'):
                    db_out.write(ff_obs80)

# -----------------------------------------------------------------
# Convenience functions for string replacement
# -----------------------------------------------------------------

def update_strs(ff_obs80, db_obs80, ff_replacement_section, db_replacement_section, r1, r2):
    '''
    MJP: 2021-05-25
    Utility function to update the sections of the ff & db strings
    '''
    if ff_replacement_section is not None and db_replacement_section is not None:
        ff_obs80 = update_str( ff_obs80, ff_replacement_section, r1,r2 )
        db_obs80 = update_str( db_obs80, db_replacement_section, r1,r2 )
    return ff_obs80, db_obs80

def update_str(original_string, replacement_section, start,finish):
    '''
    MJP: 2021-05-25
    Utility function to update a section of a string with the provided replacement_section
    '''
    assert len(replacement_section) == finish-start
    return "".join((original_string[:start],replacement_section,original_string[finish:]))

# -----------------------------------------------------------------
# Detailed functions for section-by-section "fixing" of
# obs80 strings
# -----------------------------------------------------------------

def fix_asterisk(ff_str, db_str):
    '''
    MJP: 2021-05-25
    Function to fix the asterisk field in an obs80 string
    Compare the string from the flat-file to the string from the database
    '''
    # Default
    ff_str_out , db_str_out = None, None

    # If flat-file has asterisk and the db doesn't: Assume the input flat-file is correct
    if ff_str == '*' and db_str == ' ':
        ff_str_out = db_str_out = ff_str
        
    # If flat-file does not have an asterisk, but the db does
    # *** NEED TO DECIDE WHAT TO DO
    elif ff_str == ' ' and db_str == '*':
        pass

    # If we see anything else, raise an error?
    else:
        pass
        
    return ff_str_out, db_str_out
    
def fix_note1(ff_str, db_str):
    '''
    MJP: 2021-05-25
    Function to fix the note1 field in an obs80 string
    Compare the string from the flat-file to the string from the database
    '''
    # Default
    ff_str_out , db_str_out = None, None

    # If flat-file has note and the db doesn't:
    # (1) Assume the flat-file is correct, & (2) Correct the database
    if ff_str != ' ' and db_str == ' ':
        ff_str_out = db_str_out = ff_str

    # If flat-file & db both have a note but it's different
    # CHOOSE THE FLAT-FILE ONE BASED ON THE "DEFAULT TO THE FLAT-FILE" LOGIC
    elif ff_str != ' ' and db_str != ' ' and ff_str != db_str:
        ff_str_out = db_str_out = ff_str

    # If flat-file has NO note and the db has a note:
    # (1) Assume the db is correct, & (2) Correct the flat-file
    if ff_str == ' ' and db_str != ' ':
        ff_str_out = db_str_out = db_str

    # If we see anything else, raise an error?
    else:
        pass


    return ff_str_out, db_str_out


if __name__ == '__main__':
    process_file(sys.argv[1])
