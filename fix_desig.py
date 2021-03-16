'''

I assume some command has been run like
python3 /sa/util/consistency.py /sa/mpu/UK20A.dat

I assume that output files have been created that include ...
diff_desig

'''

def analyse_pairs(line1, line2):

    # Get the designation part
    desig1 = line1[:13].strip()
    desig2 = line2[:13].strip()
    assert desig1 != desig2
    
    # Look up the primary designations in the database
    
    # If the primary designations are the same, assign to primary
    
    # If the primary designations are different, take the later one (use reference to decide which later)
    
    # If the input designation and final designation differ in their "numbered status", ...
    # ... raise a warning


def analyse_desig_file(filepath, )
    ''' go through entire diff_desig file '''
    
    # read file contents
    with open(filepath, 'r') as fh: data = fh.readlines()
    
    # check file contents
    assert len(data)  % 2 == 0
    for i, line in data[:-1] :
        assert line[15:56] == data[i+1][15:56]
        
        # analyse_pairs of lines which are duplicate
        if i % 2 == 0:
            analyse_pairs( line, data[i+1])
    
    

if __name__ == '__main__':

    # Analyse diff_desig file
    analyse_desig_file(sys.argv[1])

