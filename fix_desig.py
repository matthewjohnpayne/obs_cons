'''

I assume some command has been run like
python3 /sa/util/consistency.py /sa/mpu/UK20A.dat

I assume that output files have been created that include ...
diff_desig

'''
import os, sys
sys.path.insert(0,'/sa/identifications_pipeline/dbchecks/')
import query_ids as dbq

def analyse_pairs(line1, line2, QCID):

    # Get the designation part
    desig1 = line1[:13].strip()
    desig2 = line2[:13].strip()
    assert desig1 != desig2
    
    # Look up the primary designations in the database
    return1 = QCID.check_desig_exists(desig1)
    return2 = QCID.check_desig_exists(desig2)
    print(return1)
    print()
    print(return2)
    assert False
    
    # If the primary designations are the same, assign to primary
    
    # If the primary designations are different, take the later one (use reference to decide which later)
    
    # If the input designation and final designation differ in their "numbered status", ...
    # ... raise a warning

    
    return keep, discard

def analyse_desig_file(filepath, ):
    ''' go through entire diff_desig file '''
    keep_list,discard_list = [],[]
    
    # Init Query Class
    QCID = dbq.QueryCurrentID()

    # read file contents
    with open(filepath, 'r') as fh: data = fh.readlines()
    
    # check file contents
    assert len(data)  % 2 == 0
        
    # loop
    for i, line in enumerate(data[:-1]) :
    
        # analyse_pairs of lines which are duplicate
        if i % 2 == 0:
            # Check ...
            assert line[15:56] == data[i+1][15:56], f"line[15:56]={line[15:56]}, data[i+1][15:56]={data[i+1][15:56]}"

            # Analyze ...
            keep, discard = analyse_pairs( line, data[i+1] , QCID)
            #print('Keep   ',keep)
            #print('Discard',discard)
            #print()
            keep_list.append(keep)
            discard_list.append(discard)

    # check results
    len(discard_list) == len(keep_list) == len(data)/2
    
    # print to file
    print_to_file(discard_list, filepath+'_to_be_removed')

    return discard_list

def print_to_file(discard_list, discard_filepath):
    with open(discard_filepath, 'w') as fh:
        print('Writing observations to be deleted to ...', discard_filepath)
        for line in discard_list:
            print(line)
            lb = '\n' if line[-1] != '\n' else ''
            fh.write(line + lb)

if __name__ == '__main__':

    # Analyse diff_desig file
    analyse_desig_file(sys.argv[1])

