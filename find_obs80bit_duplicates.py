import os, sys
from itertools import islice
from collections import defaultdict



def search_for_duplicates_within_chunk( lines ):
    bit_dict       = defaultdict(list)
    duplicate_dict = {}
    for line in lines :
        if line[14] not in ['s','v','r']:
            # get the obs80 bit
            obs80bit = line[15:56]
            
            # look for duplicates
            if obs80bit in bit_dict:
                duplicate_dict[obs80bit] = True
                
            # save obs80bit, whether single or duplicate
            bit_dict[obs80bit].append(lines)
            
    # return just the duplicates
    return {k:bit_dict[k] for k in duplicate_dict}


def get_next_chunk_from_single_file( filepath , desired_len ):

    print('search_for_duplicates_within_single_file:',filepath)
    duplicate_dict = {}
    
    chunk_lines = []
    current_len = 0
        
    with open(filepath,'r') as f:
    
        while True :
        
            # Get some lines from file
            chunk_lines = list(islice(f, desired_len ))

            # Decide next step based on lengths ...
            if chunk_lines:
                yield chunk_lines
                chunk_lines = []
                current_len = 0
            else:
                break
            
def get_next_chunk_from_multiple_files( filepaths ):

    # generator to get next chunk from a file
    desired_len = int(1e7)
    gen         = get_next_chunk_from_single_file( filepaths[0] , desired_len)
    
    FINISHED = False
    while not FINISHED:
        chunk_lines = next(gen)
        FINISHED    = True if len(chunk_lines) < desired_len else False
        print(len(chunk_lines))
    
def search_for_cross_file_duplicates():
    pass
    
def search_for_duplicates( file_list ):
    assert file_list != [], 'You need to input a list of files'
        
    # We are going to process chunks of *N* lines at once
    # The *N* lines may come from one or many files
    # - We will read lines from one-or-more files until we have *N* lines in a chunk
    # We will look for duplicates that are either intra-chunk (inside) or inter-chunk (between)
    get_next_chunk_from_multiple_files( file_list )
        
    
# command-line running ...
#----------------------------------------------------
if __name__ == '__main__':

    # --- (1) : Files from the command line ---------
    assert len(sys.argv) > 2, 'You need to input a save-dir & list of files'
    assert os.path.isdir(sys.argv[1]), f'First arg [{sys.argv[1]}] not a valid directory'
    
    file_list = [ _ for _ in sys.argv[2:]]
    for _ in file_list:
        assert os.path.isfile(_), f'{_}: not a valid filepath'

    # --- (2) : Pre-defined list of primary data files ---------
    #assert len(sys.argv) > 1, 'You need to input a save-dir '
    
    
    # ---- Do the search for duplicates ----------
    search_for_duplicates( file_list )

