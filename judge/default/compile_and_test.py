import argparse
from subprocess import call

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--submission_config', type=str,
                    help="""Submission configuration file. Format of this file is:
                            SUBMISSION_ID
                            SUBMISSION_FORMAT
                            TESTCASE_1_ID
                            TESTCASE_2_ID
                            TESTCASE_3_ID
                            ...""")
args = parser.parse_args()

with open(args.submission_config) as f:
    sub_info = [x[:-1] for x in f.readlines()]

# Remove this file once used
# call(['rm', args.submission_config])

# First compile
ret = call(['./compilation_script.sh', 'submission_{}{}'.format(sub_info[0], sub_info[1])])

# If compilation fails, end this script here
if ret != 0:
    with open("submission_{}_status.txt".format(sub_info[0]), "w") as stat_file:
        for testcase_id in sub_info[2:]:
            stat_file.write("{}: {}\n".format(testcase_id, ret))
else:
    call(['./test_script.sh'] + [sub_info[0]] + sub_info[2:])
    call(['rm', 'submissions/submission_{}'.format(sub_info[0])])  # remove the executable
