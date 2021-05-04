



def search_for_duplicates_within_chunk( lines ):
    pass

def chunkify(filepath,size=1024*1024):
    ''' get start end end points of file chunks, taking care to split on newlines'''
    fileEnd = os.path.getsize(filepath)
    with open(fname,'r') as f:
        chunkEnd = f.tell()
    while True:
        chunkStart = chunkEnd
        f.seek(size,1)
        f.readline()
        chunkEnd = f.tell()
        yield chunkStart, chunkEnd - chunkStart
        if chunkEnd > fileEnd:
            break

def search_for_duplicates_within_single_file( filepath ):
    for chunkStart,chunkSize in chunkify(filepath):
        print('chunkStart,chunkSize = ',chunkStart,chunkSize)
        


    
def search_for_cross_file_duplicates():
    pass
    
def search_all( file_list ):
    assert file_list != [], 'You need to input a list of files'
    
    # find duplicates within each file
    
# command-line running ...
#----------------------------------------------------
if __name__ == '__main__':
    assert len(sys.argv) > 2, 'You need to input a save-dir & list of files'
    assert os.path.isdir(sys.argv[1]), f'First arg [{sys.argv[1]}] not a valid directory'
    
    file_list = [ _ for _ in sys.argv[2:]]
    for _ in file_list:
        assert os.path.isfile(_), f'{_}: not a valid filepath'
        
    search_all(  )

