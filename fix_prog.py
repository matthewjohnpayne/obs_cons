'''
This routine is intended to *fix* problems identified by one of PV's scripts

I assume some command has been run like
python3 /sa/util/consistency.py /sa/mpu/UK20A.dat

I assume that output files have been created that include ...
prog_cod_dup

'''
import os, sys

def analyse_pairs(line1, line2):

    # Get the program codes
    pc1 = line1[13]
    pc2 = line2[13]
    assert pc1 != pc2, f"pc1={pc1}, pc2={pc2}"
        
    # Does one have an asterisk while the other does not? Keep the asterisk!
    # *** THIS CHECK MIGHT NOT BE REQUIRED HERE, BUT NO HARM IN COPYING FROM fix_desig ***
    if   line1[12] == "*" and line2[12] != "*":
        keep, discard = line1, line2
    elif line1[12] != "*" and line2[12] == "*":
        keep, discard = line2, line1

    else:
        # If one is blank, discard (and keep the non-blank)
        if   pc1 == ' ' and pc2 != ' ':
            keep, discard = line2, line1
        elif pc1 != ' ' and pc2 == ' ':
            keep, discard = line1, line2

        # If both are not-blank, discard the first (and keep the second)
        elif pc1 != ' ' and pc2 != ' ':
            keep, discard = line2, line1
        
    return keep, discard


def analyse_prog_file(filepath, ):
    '''
    go through entire prog_cod_dup file
    
    return list of observations to be discarded
    '''
    keep_list,discard_list = [],[]
    
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
            keep, discard = analyse_pairs( line, data[i+1])
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

    # Analyse prog_cod_dup file
    analyse_prog_file( sys.argv[1] )


