import argparse
import sys

def wa_exit():
    sys.exit(1)

# Call the progarm by difffloat.py testcaseoutput.txt producedoutput.txt
if len(sys.argv) != 3:
    print('Incorrect number of arguments')
    sys.exit(2)

testcasefile = open(sys.argv[1], 'r')
outputfile = open(sys.argv[2], 'r')

testcaselines = []
try:
    for line in testcasefile.readlines():
        testcaselines.append([float(x) for x in line.strip().split()])
except ValueError:
    print('Non convertible to float')
    wa_exit()

print(testcaselines)
try:
    for i, line in enumerate(outputfile.readlines()):
        line = [float(x) for x in line.strip().split()]
        if i >= len(testcaselines) or len(testcaselines[i]) != len(line):
            print('Different number of lines or number of values on some line')
            wa_exit()
        for j, vapprox in enumerate(line):
            if abs(1 - (vapprox / testcaselines[i][j])) > 1e-6:
                # Test for relative error
                # See https://en.wikipedia.org/wiki/Approximation_error
                print('Wrong value')
                wa_exit()      
except ValueError:
    print('Non convertible to float')
    wa_exit()

# Correct answer
print('Correct answer')
sys.exit(0)
