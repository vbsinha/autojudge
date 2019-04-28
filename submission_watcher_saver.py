import os
import django

from pylint.lint import Run
from datetime import timedelta
from subprocess import call
from typing import List, Any

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pdpjudge.settings")
django.setup()

from judge import models, leaderboard  # noqa: E402

CONTENT_DIRECTORY = 'content'
TMP_DIRECTORY = 'tmp'
MONITOR_DIRECTORY = os.path.join(CONTENT_DIRECTORY, TMP_DIRECTORY)
DOCKER_VERSION = '1'
DOCKER_IMAGE_NAME = 'pdp_docker_{}'.format(DOCKER_VERSION)

LS: List[Any] = []
REFRESH_LS_TRIGGER = 10


def _compute_lint_score(error_dict):
    if error_dict['statement'] > 0:
        high = 10.0
        penalty = (5 * error_dict['error'] + error_dict['warning']) / error_dict['statement']
        high -= 10 * penalty
        return max(0.0, high)
    else:
        return 0.0


def saver(sub_id):
    update_lb = False
    # Based on the result populate SubmsissionTestCase table and return the result
    with open(os.path.join(MONITOR_DIRECTORY, 'sub_run_' + sub_id + '.txt'), 'r') as f:
        # Assumed format to sub_run_ID.txt file
        # PROBLEM_CODE
        # SUBMISSION_ID
        # TESTCASEID VERDICT TIME MEMORY MESSAGE
        # Read the output into verdict, memory and time.
        lines = [line[:-1] for line in f.readlines()]
        problem = lines[0]
        submission = lines[1]
        testcase_id, verdict, time, memory, msg = [], [], [], [], []
        for line in lines[2:]:
            sep = line.split(' ', maxsplit=4)
            testcase_id.append(sep[0])
            verdict.append(sep[1])
            time.append(sep[2])
            memory.append(sep[3])
            msg.append(sep[4] if len(sep) == 5 else '')

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
        st.memory_taken = int(memory[i])
        st.time_taken = timedelta(seconds=float(time[i]))
        if models.TestCase.objects.get(pk=testcase_id[i]).public:
            st.message = msg[i] if len(msg[i]) < 1000 else msg[i][:1000] + '\\nMessage Truncated'
        st.save()

    s.judge_score = score_received
    if s.file_type == '.py':
        penalty = Run([os.path.join(CONTENT_DIRECTORY, 'submissions',
                                    'submission_{}.py'.format(submission))], do_exit=False)
        s.linter_score = _compute_lint_score(
            penalty.linter.stats['by_module']['submission_{}'.format(submission)])
    current_final_score = s.judge_score + s.ta_score + s.linter_score

    penalty_multiplier = 1.0
    # If the submission crosses soft deadline
    # Check if the submission has crossed the hard deadline
    # If yes, penalty_multiplier = 0
    # Else, penality_multiplier = 1 - num_of_days * penalty
    remaining_time = problem.contest.soft_end_datetime - s.timestamp
    if s.timestamp > problem.contest.soft_end_datetime:
        if s.timestamp > problem.contest.hard_end_datetime:
            penalty_multiplier = 0.0
        else:
            penalty_multiplier += remaining_time.days * problem.contest.penalty

    # If num_of_days * penalty > 1.0, then the score is clamped to zero
    s.final_score = max(0.0, current_final_score * penalty_multiplier)
    s.save()

    ppf, _ = models.PersonProblemFinalScore.objects.get_or_create(person=s.participant,
                                                                  problem=problem)
    if ppf.score <= s.final_score:
        # <= because otherwise when someone submits for the first time and scores 0
        # (s)he will not show up in leaderboard
        ppf.score = s.final_score
        update_lb = True
    ppf.save()

    if update_lb and remaining_time.days >= 0:
        # Update the leaderboard only if not a late submission
        # and the submission imporved the final score
        leaderboard.update_leaderboard(problem.contest.pk, s.participant.email)

    return True


# Move to ./content
cur_path = os.getcwd()
os.chdir(os.path.join(cur_path, CONTENT_DIRECTORY))

out = 1
while out != 0:
    # Build docker image using docker run
    out = call(['docker', 'build', '-q', '-t', DOCKER_IMAGE_NAME, './'])

# Move back to old directory
os.chdir(cur_path)

print("Docker image: {} built successfully!".format(DOCKER_IMAGE_NAME))


if not os.path.exists(MONITOR_DIRECTORY):
    os.makedirs(MONITOR_DIRECTORY)


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
        os.chdir(os.path.join(cur_dir, CONTENT_DIRECTORY))

        # Run docker image
        call(['docker', 'run', '--rm', '-v', '{}:/app'.format(os.getcwd()),
              '-e', 'SUB_ID={}'.format(sub_id), DOCKER_IMAGE_NAME])

        # Come back to parent directory
        os.chdir(cur_dir)

        saver(sub_id)
        LS.remove(sub_file)
