import os, sys
from itertools import islice



def search_for_duplicates_within_chunk( lines ):
    pass


def search_for_duplicates_within_single_file( filepath , n=int(1e7) ):

    print('search_for_duplicates_within_single_file:',filepath)
    cumulative_lines = 0
    with open(filepath,'r') as f:
        while True:
            next_n_lines = list(islice(f, n))
            if not next_n_lines:
                break
            cumulative_lines += len(next_n_lines)
            print(len(next_n_lines), cumulative_lines)



    
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

