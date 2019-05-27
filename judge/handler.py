import os
import pickle

from re import compile
from io import StringIO
from logging import error as log_error
from traceback import print_exc
from csv import writer as csvwriter
from shutil import rmtree, copyfile
from datetime import timedelta, datetime
from typing import Tuple, Optional, Dict, Any, List

from django.utils import timezone
from . import models


def process_contest(name: str, contest_start: datetime, contest_soft_end: datetime,
                    contest_hard_end: datetime, penalty: float, is_public: bool,
                    enable_linter_score: bool, enable_poster_score: bool) -> Tuple[bool, str]:
    """
    Process a New Contest
    Only :attr:`penalty` can be ``None`` in which case penalty will be set to 0

    Returns:
        :code:`(True, None)` or :code:`(False, Exception string)`
    """
    try:
        c = models.Contest(name=name, start_datetime=contest_start,
                           soft_end_datetime=contest_soft_end,
                           hard_end_datetime=contest_hard_end,
                           penalty=penalty, public=is_public,
                           enable_linter_score=enable_linter_score,
                           enable_poster_score=enable_poster_score)
        c.save()
        # Successfully added to Database
        return (True, str(c.pk))
    except Exception as e:
        # Exception Case
        print_exc()
        log_error(e.__str__())
        return (False, 'Contest could not be created')


def delete_contest(contest_id: int) -> Tuple[bool, Optional[str]]:
    """
    Delete the contest.
    This will cascade delete in all the tables that have :attr:`contest_id` as a foreign key.
    It calls :func:`delete_problem` for each problem in the contest.

    Retuns:
        :code:`(True, None)`
    """
    try:
        c = models.Contest.objects.get(pk=contest_id)
        problems = models.Problem.objects.filter(contest=c)
        for problem in problems:
            delete_problem(problem.pk)
        if os.path.exists(os.path.join('content', 'contests', str(contest_id))):
            rmtree(os.path.join('content', 'contests', str(contest_id)))

        models.Contest.objects.filter(pk=contest_id).delete()
        return (True, None)
    except Exception as e:
        print_exc()
        log_error(e.__str__())
        return (False, 'Contest could not be deleted')


def process_problem(code: str, contest: int, name: str, statement: str, input_format: str,
                    output_format: str, difficulty: int, time_limit: int, memory_limit: int,
                    file_format: str, starting_code, max_score: int, compilation_script,
                    test_script) -> Tuple[bool, Optional[str]]:
    """
    Process a new Problem
    Optional fields: :attr:`starting_code`, :attr:`compilation_script`,
    :attr:`test_script`, :attr:`file_format`.

    Returns:
        :code:`(True, None)` or :code:`(False, Exception string)`
    """

    # Check if the Problem Code has already been taken
    try:
        models.Problem.objects.get(pk=code)
        return (False, '{} already a used Question code.'.format(code))
    except models.Problem.DoesNotExist:
        pass

    statement = 'The problem statement is empty.' if statement is None else statement
    input_format = 'No input format specified.' if input_format is None else input_format
    output_format = 'No output format specified.' if output_format is None else output_format

    try:
        c = models.Contest.objects.get(pk=contest)
        p = models.Problem.objects.create(
            code=code, contest=c, name=name, statement=statement,
            input_format=input_format, output_format=output_format,
            difficulty=difficulty, time_limit=time_limit, memory_limit=memory_limit,
            file_format=file_format, start_code=starting_code, max_score=max_score,
            compilation_script=compilation_script,
            test_script=test_script)

        if not os.path.exists(os.path.join('content', 'problems', p.code)):
            # Create the problem directory explictly if not yet created
            # This will happen when both compilation_script and test_script were None
            os.makedirs(os.path.join('content', 'problems', p.code))

        if compilation_script is None:
            # Copy the default comp_script if the user did not upload custom
            copyfile(os.path.join('judge', 'default', 'compilation_script.sh'),
                     os.path.join('content', 'problems', p.code, 'compilation_script.sh'))
            p.compilation_script = os.path.join('content', 'problems',
                                                p.code, 'compilation_script.sh')

        if test_script is None:
            # Copy the default test_script if the user did not upload custom
            copyfile(os.path.join('judge', 'default', 'test_script.sh'),
                     os.path.join('content', 'problems', p.code, 'test_script.sh'))
            p.test_script = os.path.join('content', 'problems', p.code, 'test_script.sh')

        # In this case, either one of compilation_script or test_script hasn't been copied
        # and saving with update the link(s)
        if compilation_script is None or test_script is None:
            p.save()

        return (True, None)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def update_problem(code: str, name: str, statement: str, input_format: str,
                   output_format: str, difficulty: str) -> Tuple[bool, Optional[str]]:
    """
    Update the fields in a problem.
    Use :attr:`code` as private key for the problem.

    Returns:
        :code:`(True, None)`
    """
    try:
        p = models.Problem.objects.get(pk=code)
        p.name = name
        p.statement = statement
        p.input_format = input_format
        p.output_format = output_format
        p.difficulty = difficulty
        p.save()
        return (True, None)
    except models.Problem.DoesNotExist:
        return (False, '{} code does not exist.'.format(code))
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def delete_problem(problem_id: str) -> Tuple[bool, Optional[str]]:
    """
    Delete the problem.
    This will cascade delete in all the tables that have :attr:`problem_id` as a foreign key.
    It will also delete all the submissions, testcases and related
    directories corresponding to the problem.

    Returns:
        :code:`(True, None)`
    """
    try:
        problem = models.Problem.objects.get(pk=problem_id)
        # First delete all the files stored corresponding to this problem
        testcases = models.TestCase.objects.filter(problem=problem)
        for testcase in testcases:
            inputfile_path = os.path.join(
                'content', 'testcase', 'inputfile_{}.txt'.format(testcase.pk))
            outputfile_path = os.path.join(
                'content', 'testcase', 'outputfile_{}.txt'.format(testcase.pk))
            if os.path.exists(inputfile_path):
                os.remove(inputfile_path)
            if os.path.exists(outputfile_path):
                os.remove(outputfile_path)
        submissions = models.Submission.objects.filter(problem=problem)
        for submission in submissions:
            submission_path = os.path.join(
                'content', 'submissions',
                'submission_{}{}'.format(submission.pk, submission.file_type))
            if os.path.exists(submission_path):
                os.remove(submission_path)
        rmtree(os.path.join('content', 'problems', problem_id))

        models.Problem.objects.filter(pk=problem_id).delete()
        return (True, None)
    except Exception as e:
        print_exc()
        log_error(e.__str__())
        return (False, 'Contest could not be deleted')


def process_person(email, rank=0) -> Tuple[bool, Optional[str]]:
    """
    Process a new Person.
    Optional Fields: :attr:`rank`.
    """
    if email is None:
        return (False, 'Email passed is None.')
    try:
        (p, status) = models.Person.objects.get_or_create(email=email)
        if status:
            p.rank = 0 if rank is None else rank
            p.save()
        return (True, None)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def process_testcase(problem_id: str, test_type: str,
                     input_file, output_file) -> Tuple[bool, Optional[str]]:
    """
    Process a new Testcase for a problem.
    :attr:`problem_id` is the primary key of the problem.

    .. warning::
        This function does not rescore all the submissions and so score will not
        change in response to the new testcase. Do not call this function once the
        contest has started, it will lead to erroneous scores.

    Returns:
        :code:`(True, None)`
    """
    try:
        problem = models.Problem.objects.get(pk=problem_id)
        t = problem.testcase_set.create(
            public=(test_type == 'public'), inputfile=input_file, outputfile=output_file)
        t.save()
        return (True, None)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def delete_testcase(testcase_id: str) -> Tuple[bool, Optional[str]]:
    """
    This function deletes the testcase and cascade deletes in
    all the tables the testcase appears.

    .. warning::
        This function does not rescore all the submissions and so score will not
        change in response to the deleted testcase. Do not call this function once the
        contest has started, it will lead to erroneous scores.

    Returns:
        :code:`(True, None)`
    """
    try:
        inputfile_path = os.path.join(
            'content', 'testcase', 'inputfile_{}.txt'.format(testcase_id))
        outputfile_path = os.path.join(
            'content', 'testcase', 'outputfile_{}.txt'.format(testcase_id))
        if os.path.exists(inputfile_path):
            os.remove(inputfile_path)
        if os.path.exists(outputfile_path):
            os.remove(outputfile_path)
        models.TestCase.objects.filter(pk=testcase_id).delete()
        return (True, None)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def process_submission(problem_id: str, participant: str, file_type,
                       submission_file, timestamp: str) -> Tuple[bool, Optional[str]]:
    """
    Process a new submission.
    :attr:`problem_id` is the primary key of the problem.
    :attr:`participant` is the email (which is the primary key) of the participant.
    """
    try:
        problem = models.Problem.objects.get(pk=problem_id)
        if file_type not in problem.file_format.split(','):
            return (False, 'Accepted file types: \"{}\"'
                           .format(', '.join(problem.file_format.split(','))))
        participant = models.Person.objects.get(email=participant)
        s = problem.submission_set.create(participant=participant, file_type=file_type,
                                          submission_file=submission_file, timestamp=timestamp)
        s.save()
    except Exception as e:
        print_exc()
        return (False, e.__str__())

    testcases = models.TestCase.objects.filter(problem=problem)

    if not os.path.exists(os.path.join('content', 'tmp')):
        os.makedirs(os.path.join('content', 'tmp'))
    # NB: File structure here
    # PROBLEM_ID
    # SUBMISSION_ID
    # FILE_FORMAT
    # TIME_LIMIT
    # MEMORY_LIMIT
    # TESTCASE_1
    # TESTCASE_2
    # ....
    with open(os.path.join('content', 'tmp', 'sub_run_' + str(s.pk) + '.txt'), 'w') as f:
        f.write('{}\n'.format(problem.pk))
        f.write('{}\n'.format(s.pk))
        f.write('{}\n'.format(file_type))
        f.write('{}\n'.format(int(problem.time_limit.total_seconds())))
        f.write('{}\n'.format(problem.memory_limit))
        for testcase in testcases:
            f.write('{}\n'.format(testcase.pk))

    try:
        for testcase in testcases:
            models.SubmissionTestCase.objects.create(submission=s, testcase=testcase,
                                                     verdict='R', memory_taken=0,
                                                     time_taken=timedelta(seconds=0))
    except Exception as e:
        print_exc()
        return (False, e.__str__())

    return (True, None)


def update_poster_score(submission_id: str, new_score: int):
    """
    Updates the poster score for a submission.
    :attr:`submission_id` is the primary key of the submission and :attr:`new_score`
    is the new poster score.
    Leaderboard is updated if the new score for the person-problem pair has changed.

    Returns:
        :code:`(True, None)` or :code:`(False, Exception string)`
    """
    try:
        submission = models.Submission.objects.get(pk=submission_id)
        submission.final_score -= submission.poster_score
        submission.poster_score = new_score
        submission.final_score += submission.poster_score
        submission.save()

        highest_scoring_submission = models.Submission.objects.filter(
            problem=submission.problem.pk, participant=submission.participant.pk).\
            order_by('-final_score').first()
        ppf, _ = models.PersonProblemFinalScore.objects.get_or_create(
            person=submission.participant, problem=submission.problem)
        old_highscore = ppf.score
        ppf.score = highest_scoring_submission.final_score
        ppf.save()

        if old_highscore != ppf.score:
            # Update the leaderboard only if submission imporved the final score
            update_leaderboard(submission.problem.contest.pk,
                               submission.participant.email)
        return (True, None)
    except Exception as e:
        return (False, e.__str__())


def add_person_to_contest(person: str, contest: str,
                          permission: bool) -> Tuple[bool, Optional[str]]:
    """
    Add the relation between Person and Contest.
    :attr:`person` is the email of the person.
    :attr:`contest` is the primary key of the contest.
    :attr:`permission` is ``False`` if participant or ``True`` if poster.
    """
    try:
        (p, _) = models.Person.objects.get_or_create(email=person)
        c = models.Contest.objects.get(pk=contest)
        if c.public is True and permission is False:
            # Do not store participants for public contests
            return (True, None)
        try:
            # Check that the person is not already registered in the contest with other permission
            cp = models.ContestPerson.objects.get(person=p, contest=c)
            if cp.role == permission:
                return (False, '{} is already a {}'.format(
                    p.email, 'Poster' if permission else 'Participant'))
            else:
                return (False, '{} already exists with other permission'.format(p.email))
        except models.ContestPerson.DoesNotExist:
            cp = p.contestperson_set.create(contest=c, role=permission)
            cp.save()
            return (True, None)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def add_person_rgx_to_contest(rgx: str, contest: str,
                              permission: bool) -> Tuple[bool, Optional[str]]:
    """
    Accepts a regex and adds all the participants matching the regex in the database to the contest
    with the permission given by :attr:`permission`.
    Note that unlike :func:`add_person_to_contest`, this function does not create any new persons.
    See example usage below:

    >>> add_person_rgx_to_contest('cs15btech*', 'C1', True)

    Returns:
        :code:`(True, None)` if there is at least one match

        :code:`(False, error)` if no match

    """
    pattern = compile(rgx)
    try:
        person_emails = [p.email for p in models.Person.objects.all()]
        emails_matches = [email for email in person_emails if bool(pattern.match(email))]
        c = models.Contest.objects.get(pk=contest)
        if c.public is True and permission is False:
            # Do not store participants for public contests
            return (True, None)
        if len(emails_matches) == 0:
            return (False, 'Regex {} did not match any person registered'.format(rgx))
        for email in emails_matches:
            add_person_to_contest(email, contest, permission)
        return (True, None)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def add_persons_to_contest(persons: List[str], contest: str,
                           permission: bool) -> Tuple[bool, Optional[str]]:
    """
    Add the relation between Person and Contest for all the Person in :attr:`persons`.
    :attr:`persons` is the list of email of persons.
    :attr:`contest` is the primary key of the contest.
    :attr:`permission` is ``False`` if participant or ``True`` if poster.

    .. note::
        First check if any of the person exists with an opposing role.
        If so, do not add anyone. Instead return a tuple with ``False`` and
        and an appropriate message.
        Otherwise if person doesn't have conflicting permission,
        add all the persons and return :code:`(True, None)`.

    This function would create records for all the persons who do not already have one irrespective
    of whether anyone has conflict or not.
    """
    try:
        for person in persons:
            models.Person.objects.get_or_create(email=person)

        c = models.Contest.objects.get(pk=contest)
        if c.public is True and permission is False:
            # Do not store participants for public contests
            return (True, None)

        person_list = [models.Person.objects.get(email=person) for person in persons]
        for p in person_list:
            try:
                # Check that person is not already registered in the contest with other permission
                cp = models.ContestPerson.objects.get(person=p, contest=c)
                if cp.role == (not permission):
                    return (False, '{} already exists with other permission'.format(p.email))
            except models.ContestPerson.DoesNotExist:
                continue

        for p in person_list:
            models.ContestPerson.objects.get_or_create(contest=c, person=p, role=permission)
        return (True, None)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def get_personcontest_permission(person: Optional[str], contest: int) -> Optional[bool]:
    """
    Determine the relation between Person and Contest.
    :attr:`person` is the email of the person.
    :attr:`contest` is the primary key of the contest.

    Returns:
        ``False`` if participant, ``True`` if poster and ``None`` if neither.
    """
    curr = timezone.now()
    if person is None:
        try:
            c = models.Contest.objects.get(pk=contest)
            if c.public and curr >= c.start_datetime:
                return False
            else:
                return None
        except Exception:
            return None
    p = models.Person.objects.get(email=person)
    c = models.Contest.objects.get(pk=contest)
    # participant and Current datetime < C.date_time -> None
    try:
        cp = models.ContestPerson.objects.get(person=p, contest=c)
        if cp.role is False and curr < c.start_datetime:
            return None
        return cp.role
    except models.ContestPerson.DoesNotExist:
        if c.public and curr >= c.start_datetime:
            return False
    except Exception:
        return None
    return None


def delete_personcontest(person: str, contest: str) -> Tuple[bool, Optional[str]]:
    """
    Delete the record of :attr:`person` and :attr:`contest` in the
    :class:`~judge.models.ContestPerson` table.
    Passed email in :attr:`person` and :attr:`contest` is the primary key.

    Returns:
        :code:`(True, None)`
    """
    try:
        p = models.Person.objects.get(email=person)
        c = models.Contest.objects.get(pk=contest)
        cpset = models.ContestPerson.objects.filter(person=p, contest=c)
        if cpset.exists():
            cp = cpset[0]
            if (cp.role is False) or \
               (models.ContestPerson.objects.filter(contest=c, role=True).count() > 1):
                # If the person to be deleted is a participant or there are more than 1 posters
                # then we can delete the record from db.
                cpset.delete()
            else:
                return (False, 'This contest cannot be orphaned!')
        return (True, None)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def get_personproblem_permission(person: Optional[str], problem: str) -> Optional[bool]:
    """
    Determine the relation between a Person and a Problem.
    :attr:`person` is the email of the person.
    :attr:`problem` is the primary key of the problem.

    Returns:
        ``False`` if participant, ``True`` if poster and ``None`` if neither.
    """
    p = models.Problem.objects.get(pk=problem)
    if p.contest is None:
        return False
    return get_personcontest_permission(person, p.contest.pk)


def get_posters(contest) -> Tuple[bool, Optional[str]]:
    """
    Return the posters for a contest.
    :attr:`contest` is the primary key of the Contest.

    Returns:
        :code:`(True, List of the email of the posters)`
    """
    try:
        c = models.Contest.objects.get(pk=contest)
        cps = models.ContestPerson.objects.filter(contest=c, role=True)
        cps = [cp.person.email for cp in cps]
        return (True, cps)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def get_participants(contest) -> Tuple[bool, Any]:
    """
    Return the participants for the contest.
    :attr:`contest` is the primary key of the Contest.

    Returns:
        :code:`(True, List of the email of the participants)` if contest is private.

        :code:`(True, [])` if contest is public.
    """
    try:
        c = models.Contest.objects.get(pk=contest)
        if c.public is True:
            return (True, [])
        cps = models.ContestPerson.objects.filter(contest=c, role=False)
        cps = [cp.person.email for cp in cps]
        return (True, cps)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def get_personcontest_score(person: str, contest: int) -> Tuple[bool, Any]:
    """
    Get the final score which is the sum of individual final scores of all problems in the contest.
    Pass email in :attr:`person` and primary key of contest.
    """
    try:
        p = models.Person.objects.get(email=person)
        c = models.Contest.objects.get(pk=contest)
        problems = models.Problem.objects.filter(contest=c)
        score = 0
        for problem in problems:
            score += models.PersonProblemFinalScore.objects.get(
                person=p, problem=problem).score
        return (True, score)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def get_submission_status(person: str, problem: str, submission):
    """
    Get the current status of the submission.
    Pass email as :attr:`person` and problem code as :attr:`problem` to get a tuple.
    In case :attr:`submission` is ``None``,

    Returns :code:`(True, (dict1, dict2))`
        The tuple consists of 2 dictionaries:

        First dictionary:
            Key: Submission ID

            Value: :code:`(TestcaseID, Verdict, Time_taken, Memory_taken, ispublic, message)` list

        Second dictionary:
            Key: Submission ID

            Value: :code:`(judge_score, poster_score, linter_score,
                           final_score, timestamp, file_type)`

    In case :attr:`submission` is not ``None``, the passed parameters :attr:`person`
    and :attr:`problem` are ignored and so ``None`` is accepted.

    Returns:
        The same dictionaries in a tuple but having only 1 key in both
    """
    try:
        if submission is None:
            p = models.Person.objects.get(email=person)
            q = models.Problem.objects.get(code=problem)
            sub_list = models.Submission.objects.filter(
                participant=p, problem=q).order_by('-timestamp')
            t = models.TestCase.objects.filter(problem=p)
        else:
            submission = models.Submission.objects.get(pk=submission)
            t = models.TestCase.objects.filter(problem=submission.problem)
            sub_list = [submission]
    except Exception as e:
        print_exc()
        return (False, e.__str__())

    verdict_dict: Dict[Any, Any] = dict()
    score_dict = dict()

    for submission in sub_list:
        score_dict[submission.pk] = (submission.judge_score, submission.poster_score,
                                     submission.linter_score, submission.final_score,
                                     submission.timestamp, submission.file_type)
        verdict_dict[submission.pk] = []
        try:
            for testcase in t:
                st = models.SubmissionTestCase.objects.get(
                    submission=submission, testcase=testcase)
                verdict_dict[submission.pk].append((testcase.pk, st.verdict, st.time_taken,
                                                    st.memory_taken, testcase.public, st.message))
        except Exception:
            # In case Exception occurs for any submission, then
            # that submission's verdict_dict is left empty.
            # This is done to allow the other submissions to give output.
            print_exc()
    return (True, (verdict_dict, score_dict))


def get_submissions(problem_id: str, person_id: Optional[str]) -> Tuple[bool, Any]:
    """
    Get all the submissions for this problem by this (or all) persons who attempted.
    :attr:`problem` is the primary key of the Problem.
    :attr:`person_id` is the email of the Person or ``None``
    if you want to retrieve submissions by all participants.

    Returns:
        when :attr:`person_id` is ``None``:
            :code:`(True, {emailofperson: [SubmissionObject1, SubmissionObject2, ...],` \
            :code:`emailofperson: [SubmissionObjecti, SubmissionObjectj, ...], ...})`

        when :attr:`person_id` is not ``None``:
            :code:`(True, {emailofperson: [SubmissionObject1, SubmissionObject2, ...]})`
    """
    try:
        p = models.Problem.objects.get(code=problem_id)
        if person_id is None:
            submission_set = models.Submission.objects.filter(
                problem=p).order_by('participant')
        else:
            person = models.Person.objects.get(email=person_id)
            submission_set = models.Submission.objects.filter(
                problem=p, participant=person).order_by('participant')
        result = {}
        if submission_set.count() == 0:
            if person_id is None:
                return (True, {})
            else:
                return (True, {person.pk: []})
        curr_person = submission_set[0].participant.pk
        result[curr_person] = [submission_set[0]]
        for i in range(1, len(submission_set)):
            if submission_set[i].participant.pk == curr_person:
                result[curr_person].append(submission_set[i])
            else:
                curr_person = submission_set[i].participant.pk
                result[curr_person] = [submission_set[i]]
        return (True, result)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def get_submission_status_mini(submission: str) -> Tuple[bool, Any]:
    """
    Get the current status of the submission.

    Returns:
        :code:`(True, (dict1, tuple1))`

    The tuple consists of a dictionary and a tuple:
        Dictionary:
            Key: TestcaseID

            Value: :code:`(Verdict, Time_taken, Memory_taken, ispublic, message)`
        Tuple:
            :code:`(judge_score, poster_score, linter_score, final_score, timestamp, file_type)`
    """
    try:
        s = models.Submission.objects.get(pk=submission)
        testcases = models.TestCase.objects.filter(problem=s.problem)

        verdict_dict: Dict[Any, Any] = dict()

        for testcase in testcases:
            st = models.SubmissionTestCase.objects.get(
                submission=s, testcase=testcase)
            verdict_dict[testcase.pk] = (st.get_verdict_display, st.time_taken,
                                         st.memory_taken, testcase.public, st.message)
        score_tuple = (s.judge_score, s.poster_score, s.linter_score, s.final_score,
                       s.timestamp, s.file_type)
        return (True, (verdict_dict, score_tuple))
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def get_leaderboard(contest: int) -> Tuple[bool, Any]:
    """
    Returns the current leaderboard for the passed contest.
    :attr:`contest` is the primary key for contest.

    Returns:
        :code:`(True, [[Rank1Email, ScoreofRank1], [Rank2Email, ScoreofRank2] ... ])`
    """
    leaderboard_path = os.path.join('content', 'contests', str(contest)+'.lb')
    if not os.path.exists(leaderboard_path):
        return (False, 'Leaderboard not yet initialized for this contest.')
    try:
        with open(leaderboard_path, 'rb') as f:
            data = pickle.load(f)
        return (True, data)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def update_leaderboard(contest: int, person: str):
    """
    Updates the leaderboard for the passed contest for the rank of the person.
    :attr:`contest` is the primary key of the contest and :attr:`person` is the email of person.
    Only call this function when some submission for some problem of the contest
    has scored more than its previous submission.
    Remember to call this function whenever
    :class:`~judge.models.PersonProblemFinalScore` is updated.

    Returns:
        ``True`` if update was successful, ``False`` otherwise
    """

    os.makedirs(os.path.join('content', 'contests'), exist_ok=True)
    pickle_path = os.path.join('content', 'contests', str(contest) + '.lb')

    status, score = get_personcontest_score(person, contest)

    if status:
        if not os.path.exists(pickle_path):
            with open(pickle_path, 'wb') as f:
                data = [[person, score]]
                pickle.dump(data, f)
            return True
        else:
            with open(pickle_path, 'rb') as f:
                data = pickle.load(f)
            with open(pickle_path, 'wb') as f:
                for i in range(len(data)):
                    if data[i][0] == person:
                        data[i][1] = score
                        break
                else:
                    data.append([person, score])
                data = sorted(data, key=lambda x: x[1], reverse=True)
                pickle.dump(data, f)
            return True
    else:
        return False


def process_comment(problem: str, person: str, commenter: str,
                    timestamp, comment: str) -> Tuple[bool, Optional[str]]:
    """
    Privately comment :attr:`comment` on the problem for person by commenter.
    :attr:`problem` is the primary key of the Problem.
    :attr:`person` and :attr:`commenter` are emails of Person.

    Returns:
        :code:`(True, None)`
    """
    try:
        problem = models.Problem.objects.get(pk=problem)
        person = models.Person.objects.get(email=person)
        commenter = models.Person.objects.get(email=commenter)
        models.Comment.objects.create(problem=problem, person=person,
                                      commenter=commenter, timestamp=timestamp, comment=comment)
        return (True, None)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def get_comments(problem: str, person: str) -> Tuple[bool, Any]:
    """
    Get the private comments on the problem for the person.

    Returns:
        :code:`(True, [(Commeter, Timestamp, Comment) ... (Sorted in chronological order)])`
    """
    try:
        comments = models.Comment.objects.filter(
            problem=problem, person=person).order_by('timestamp')
        result = [(comment.commenter, comment.timestamp, comment.comment)
                  for comment in comments]
        return (True, result)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def get_csv(contest: str) -> Tuple[bool, Any]:
    """
    Get the CSV (in string form) of the current scores of all participants in the contest.
    Pass primary key of the contest.

    Returns:
        :attr:`(True, csvstring)`
    """
    try:
        c = models.Contest.objects.get(pk=contest)
        problems = models.Problem.objects.filter(contest=c)

        csvstring = StringIO()
        writer = csvwriter(csvstring)
        writer.writerow(['Email', 'Score'])

        if problems.exists():
            # Get the final scores for each problem for any participant who has attempted.
            submissions = models.PersonProblemFinalScore.objects.filter(problem=problems[0])
            for problem in problems[1:]:
                submissions |= models.PersonProblemFinalScore.objects.filter(problem=problem)

            if submissions.exists():
                # Now sort all the person-problem-scores by 'person' and 'problem'
                # This will create scores like:
                # [('p1', 3(Say score corresponding to problem2)),
                #  ('p1', 2(score corresponding to problem4)),
                #  ('p2', 5(score corresponding to problem3)),
                #  ('p2', 0(score corresponding to problem1)) ... ]
                # We do not need to save exactly which problem the score correspondes to
                # we only need to know scores on all problems by a participant
                submissions.order_by('person', 'problem')
                scores = [(submission.person, submission.score)
                          for submission in submissions]

                # Here we aggregate the previous list.
                # We simply iterate over scores and for each participant,
                # we sum up how much has he scored in all the problems.
                # To do this we exploit the fact that list is already sorted.
                # In the above case after aggregating we'll write
                # 'p1', 5
                # 'p2', 5 etc. in csvstring
                curr_person = scores[0][0]
                sum_scores = 0
                for score in scores:
                    if curr_person == score[0]:
                        sum_scores += score[1]
                    else:
                        writer.writerow([curr_person, sum_scores])
                        curr_person = score[0]
                        sum_scores = score[1]
                writer.writerow([curr_person, sum_scores])

        csvstring.seek(0)
        return (True, csvstring)
    except Exception as e:
        print_exc()
        return (False, e.__str__())
