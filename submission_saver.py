import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pdpjudge.settings")
django.setup()

from judge import models

def saver(subid):
    # Based on the result populate SubmsissionTestCase table and return the result
    with open(os.path.join('content', 'tmp', 'sub_run_'+subid+'.txt'), 'r') as f:
        # Assumed format to sub_run_ID.txt file
        # PROBLEM_CODE
        # SUBMISSION_ID
        # SUBMISSION_FORMAT
        # TESTCASEID VERDICT TIME MEMORY
        # Read the output into verdict, memory and time.
        problem = f.readline()
        submission = f.readline()
        sub_format = f.readline()
        testcase_id, verdict, time, memory = [], [], [], []
        for line in f:
            sep = line.split()
            testcase_id.append(sep[0])
            verdict.append(sep[1])
            memory.append(sep[2])
            time.append(sep[3])
        # Also collect Compilation / Runtime Error for Public testcases

    # Delete the file after reading
    os.remove(os.path.join('content', 'tmp', 'sub_run_'+subid+'.txt'))

    problem = models.Problem.objects.get(pk=problem)
    s = models.Submission.objects.get(pk=submission)
    # testcases = models.TestCase.objects.get(problem=problem)

    score_recieved = 0
    max_score = problem.max_score
    for i in range(len(testcase_id)):
        if verdict[i] == 'P':
            score_recieved += max_score
        st = models.SubmissionTestCase.objects.get(
            submission=submission, testcase=testcase_id[i])
        st.verdict = verdict[i]
        st.memory_taken = memory[i]
        st.time_taken = time[i]
        st.save()

    s.judge_score = score_recieved
    s.final_score = s.judge_score + s.ta_score + s.linter_score
    s.save()
    return True
