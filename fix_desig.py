'''

I assume some command has been run like
python3 /sa/util/consistency.py /sa/mpu/UK20A.dat

I assume that output files have been created that include ...
diff_desig

'''
import os, sys
sys.path.insert(0,'/sa/identifications_pipeline/dbchecks/')
import query_ids as dbq

def get_desig(line):
    
    # Unnumbered
    if line[:5].strip() == '':
        packed_desig   = line[5:].strip()
        unpacked_desig = mpc_convert.packed_to_unpacked_desig(packed_desig)
        NUMBERED = False
    # Numbered
    else:
        packed_desig   = line[:5].strip()
        unpacked_desig = mpc_convert.packed_to_unpacked_desig(packed_desig)
        unpacked_desig = ''.join([_ for _ in unpacked_desig if _ not in [')','('] ])
        while unpacked_desig[0] == '0':
            unpacked_desig = unpacked_desig[1:]
        assert len(unpacked_desig)
        NUMBERED = True

    return unpacked_desig , packed_desig, NUMBERED

def analyse_pairs(line1, line2, QCID):

    # Get the designation part (can be numbered or unnumbered)
    unpacked_desig1 , packed_desig1, NUMBERED1 = get_desig(line1)
    unpacked_desig2 , packed_desig2, NUMBERED2 = get_desig(line2)
    ref1 = line1[72:77].strip()
    ref2 = line2[72:77].strip()
    print(f'unpacked_desig1 , packed_desig1, NUMBERED1 = {unpacked_desig1 , packed_desig1, NUMBERED1}')
    # Look up the primary designations in the database
    if NUMBERED1:
        prim1 = QCID.get_packed_desig_from_number(unpacked_desig1)
    else:
        prim1 = QCID.check_desig_exists(desig1)[0]['packed_primary_provisional_designation']
    sys.exit(f'prim1={prim1}')
    if NUMBERED2:
        prim2 = QCID.get_packed_desig_from_number(unpacked_desig2)
    else:
        prim2 = QCID.check_desig_exists(desig1)[0]['packed_primary_provisional_designation']

    # Does one have an asterisk while the other does not? Keep the asterisk!
    if   line1[12] == "*" and line2[12] != "*":
        keep, discard = line1, line2
    elif line1[12] != "*" and line2[12] == "*":
        keep, discard = line2, line1

    else:
    
        # If there's an obvious redesignation...
        if   desig1 in line2:
            keep, discard = line2, line1
        elif desig2 in line1:
            keep, discard = line1, line2
        else:
        
            # Take the later one (use reference to decide which later)
            if ref2 >= ref1:
                keep, discard = line2, line1
            else:
                keep, discard = line1, line2
        
    return keep, discard

def analyse_desig_file(filepath, ):
    ''' go through entire diff_desig file '''
    keep_list,discard_list = [],[]
    
    # Init Query Class
    QCID = dbq.QueryCurrentID()

    # read file contents
    with open(filepath, 'r') as fh:
        data = [_.strip('\n') for _ in fh.readlines()]
    
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

