import os
import django

from subprocess import call

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pdpjudge.settings")
django.setup()

from judge import models  # noqa: E402

MONITOR_DIRECTORY = os.path.join('content', 'tmp')
DOCKER_IMAGE_NAME = 'pdp_docker'

LS = []
REFRESH_LS_TRIGGER = 10


def saver(sub_id):
    # Based on the result populate SubmsissionTestCase table and return the result
    with open(os.path.join(MONITOR_DIRECTORY, 'sub_run_' + sub_id + '.txt'), 'r') as f:
        # Assumed format to sub_run_ID.txt file
        # PROBLEM_CODE
        # SUBMISSION_ID
        # TESTCASEID VERDICT TIME MEMORY MESSAGE
        # Read the output into verdict, memory and time.
        problem = f.readline()
        submission = f.readline()
        testcase_id, verdict, time, memory, msg = [], [], [], [], []
        for line in f:
            sep = line.split(' ', maxsplit=4)
            testcase_id.append(sep[0])
            verdict.append(sep[1])
            memory.append(sep[2])
            time.append(sep[3])
            msg.append(sep[4])

    # Delete the file after reading
    os.remove(os.path.join(MONITOR_DIRECTORY, 'sub_run_' + sub_id + '.txt'))

    problem = models.Problem.objects.get(pk=problem)
    s = models.Submission.objects.get(pk=submission)

    score_received = 0
    max_score = problem.max_score
    for i in range(len(testcase_id)):
        if verdict[i] == 'P':
            score_received += max_score
        st = models.SubmissionTestCase.objects.get(submission=submission,
                                                   testcase=testcase_id[i])
        st.verdict = verdict[i]
        st.memory_taken = memory[i]
        st.time_taken = time[i]
        if models.TestCase.objects.get(pk=testcase_id[i]).public:
            st.message = msg[i] if len(msg[i]) < 1000 else msg[i][:1000] + '\\nMessage Truncated'
        st.save()

    s.judge_score = score_received
    s.final_score = s.judge_score + s.ta_score + s.linter_score
    s.save()
    return True


# Watcher loop
while True:
    if len(LS) < REFRESH_LS_TRIGGER:
        LS = [os.path.join(MONITOR_DIRECTORY, sub_file)
              for sub_file in os.listdir(MONITOR_DIRECTORY)]
        LS.sort(key=os.path.getctime)

    if len(LS) > 0:
        sub_file = LS[0]  # The first file submission-wise
        sub_id = os.path.basename(sub_file)[8:-4]  # This is the submission ID

        # Move to content
        cur_dir = os.getcwd()
        os.chdir(os.path.join(cur_dir, 'content'))

        # Run docker image
        call(['docker', 'run', '--rm', '-v', '{}:/app'.format(os.getcwd()),
              '-e', 'SUB_ID={}'.format(sub_id), DOCKER_IMAGE_NAME])

        # Come back to parent directory
        os.chdir(cur_dir)

        saver(sub_id)
        LS.remove(sub_file)
