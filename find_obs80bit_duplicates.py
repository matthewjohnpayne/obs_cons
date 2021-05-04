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


def search_for_duplicates_within_single_file( filepath , n=int(1e7) ):

    print('search_for_duplicates_within_single_file:',filepath)
    cumulative_lines = 0
    duplicate_dict = {}
    with open(filepath,'r') as f:
        while True:
        
            # Get next chunk
            next_n_lines = list(islice(f, n))
            if not next_n_lines:
                break
                
            # Keep a count of the lines / progress
            cumulative_lines += len(next_n_lines)
            print(len(next_n_lines), cumulative_lines)
            
            # Look for duplicates within a chunk
            duplicate_dict.update(  search_for_duplicates_within_chunk( lines ) )
            print( len(duplicate_dict) )

            
    
def search_for_cross_file_duplicates():
    pass
    
def search_all( file_list ):
    assert file_list != [], 'You need to input a list of files'
    
    # find duplicates within each file
    for filepath in file_list:
        search_for_duplicates_within_single_file( filepath )
    
# command-line running ...
#----------------------------------------------------
if __name__ == '__main__':
    assert len(sys.argv) > 2, 'You need to input a save-dir & list of files'
    assert os.path.isdir(sys.argv[1]), f'First arg [{sys.argv[1]}] not a valid directory'
    
    file_list = [ _ for _ in sys.argv[2:]]
    for _ in file_list:
        assert os.path.isfile(_), f'{_}: not a valid filepath'
        
    search_all( file_list )

