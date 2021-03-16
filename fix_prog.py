'''

I assume some command has been run like
python3 /sa/util/consistency.py /sa/mpu/UK20A.dat

I assume that output files have been created that include ...
prog_cod_dup

'''

def analyse_pairs(line1, line2):

    # Get the program codes
    pc1 = line1[14]
    pc2 = line2[14]
    assert pc1 != pc2
        
    # If one is blank, discard (and keep the non-blank)
    if   pc1 == ' ' and pc2 != ' ':
        keep, discard = line2, line1
    elif pc1 != ' ' and pc2 == ' ':
        keep, discard = line1, line2

    # If both are not-blank, discard the first (and keep the second)
    elif pc1 != ' ' and pc2 != ' ':
        keep, discard = line2, line1
    
    return keep, discard


def analyse_prog_file(filepath, )
    ''' go through entire prog_cod_dup file '''
    keep_list,discard_list = [],[]
    
    # read file contents
    with open(filepath, 'r') as fh: data = fh.readlines()
    
    # check file contents
    assert len(data)  % 2 == 0
    for i, line in data[:-1] :
        assert line[15:56] == data[i+1][15:56]
        
        # analyse_pairs of lines which are duplicate
        if i % 2 == 0:
            keep, discard = analyse_pairs( line, data[i+1])
            keep_list.append(keep)
            discard_list.append(keep)
    
    # check results
    len(discard_list) == len(keep_list) == len(data)/2
    
    for _ in discard_list:
        print(_)
        
    return discard_list

"""
def remove_discards(filepath , discard_list):
    ''' go through filepath and remove items that are in discard_list '''

    # read file contents
    with open(filepath, 'r') as fh: data = fh.readlines())
    
    # discard ...
    subset = [ _ for _ in data if _ not in discard_list ]
    
    # check...
    assert len(subset) + len(discard_list) == len(data)
        
    # write out (to separate file for now)
    with open(filepath+'tmp', 'w') as fh:
        for _ in subset:
            fh.write(_)
"""


if __name__ == '__main__':

    # Analyse prog_cod_dup file
    analyse_prog_file(sys.argv[1])


