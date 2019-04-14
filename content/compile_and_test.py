import argparse
import subprocess

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--submission_config', type=str,
                    help="""Submission configuration file. Format of this file is:
                            PROBLEM_CODE
                            SUBMISSION_ID
                            SUBMISSION_FORMAT
                            TESTCASE_1_ID
                            TESTCASE_2_ID
                            TESTCASE_3_ID
                            ...""")
args = parser.parse_args()

with open(args.submission_config) as f:
    sub_info = [x[:-1] for x in f.readlines()]

# Retain the first 2 lines alone
subprocess.call(['rm', args.submission_config])
with open(args.submission_config, "w") as stat_file:
    stat_file.write("{}\n{}\n".format(sub_info[0], sub_info[1]))

# First compile
try:
    subprocess.check_output(['./main_compiler.sh', sub_info[0],
                             'submission_{}{}'.format(sub_info[1], sub_info[2])],
                            stderr=subprocess.STDOUT)
except subprocess.CalledProcessError as e:  # If compilation fails, end this script here
    error_msg = e.output.decode('utf-8').replace('\n', '\\n')
    with open(args.submission_config, "a") as stat_file:
        for testcase_id in sub_info[3:]:
            stat_file.write("{} {} 0 0 {}\n"
                            .format(testcase_id,
                                    'CE' if e.returncode == 1 else 'NA',
                                    error_msg))
else:
    subprocess.call(['./main_tester.sh'] + sub_info[0:2] + sub_info[3:])  # run tests
    subprocess.call(['rm', 'submissions/submission_{}'.format(sub_info[1])])  # remove executable
