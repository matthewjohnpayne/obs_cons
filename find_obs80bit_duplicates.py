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

    print('\t\t\t get_next_chunk_from_single_file:',filepath, ' , desired_len=', desired_len)
    duplicate_dict = {}
        
    with open(filepath,'r') as f:
    
        while True :
        
            # Get some lines from file
            chunk_lines = list(islice(f, desired_len ))

            # If anything comes back, then yield ...
            if chunk_lines:
                yield [ (filepath, _) for _ in chunk_lines ]
            else:
                break
            
def get_next_chunk_from_multiple_files( filepaths , desired_len):

    print("get_next_chunk_from_multiple_files:")
    
    chunk_len   = 0
    chunk_lines = []
    for filepath in filepaths:
        print('\t', filepath)
        # generator to get next chunk from file
        gen         = get_next_chunk_from_single_file( filepath , desired_len - chunk_len  )
                
        while True:
        
            # extract a chunk from file
            file_chunk_lines = next(gen)
            
            # extend master chunk
            chunk_lines.extend( file_chunk_lines )
            chunk_len = len(chunk_lines)
                        
            # yield if we already have enough data
            if len(chunk_lines) >= desired_len:
                print('\t\tDEBUG1', chunk_len , desired_len, chunk_len == desired_len)
                yield chunk_lines
                chunk_lines = []
            else:
                print('\t\tDEBUG2', chunk_len , desired_len, chunk_len == desired_len)
                break
            
    return chunk_lines
    
    
def search_for_duplicates( file_list ):
    print('search_for_duplicates')
    print('sss\n'*123)
    
    assert file_list != [], 'You need to input a list of files'
        
    # We are going to process chunks of *N* lines at once
    # The *N* lines may come from one or many files
    # - We will read lines from one-or-more files until we have *N* lines in a chunk
    # We will look for duplicates that are either intra-chunk (inside) or inter-chunk (between)
    desired_len = int(1e7)
    gen         = get_next_chunk_from_multiple_files( file_list , desired_len )

    FINISHED = False
    while not FINISHED:
        print('Looping within search_for_duplicates ... ')
        chunk_lines = next(gen)
        #FINISHED    = True if len(chunk_lines) < desired_len else False
        #print(len(chunk_lines) , '\n\t', chunk_lines[0], '\n\t', chunk_lines[-1])
    

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

