import os
import pickle

from re import compile
from io import StringIO
from traceback import print_exc
from csv import writer as csvwriter
from shutil import rmtree, copyfile
from logging import error as log_error
from datetime import timedelta, datetime
from typing import Tuple, Optional, Dict, Any, List, Union

from django.utils import timezone
from django.core.files.uploadedfile import InMemoryUploadedFile

from . import models


def _check_and_remove(*fullpaths):
    for fullpath in fullpaths:
        if os.path.exists(fullpath):
            os.remove(fullpath)


def process_contest(contest_name: str, contest_start: datetime, contest_soft_end: datetime,
                    contest_hard_end: datetime, penalty: float, is_public: bool,
                    enable_linter_score: bool, enable_poster_score: bool) -> Tuple[bool, str]:
    """
    Function to process a new :class:`~judge.models.Contest`.

    :param contest_name: Name of the contest
    :param contest_start: A `datetime` object representing the beginning of the contest
    :param contest_soft_end: A `datetime` object representing the soft deadline of the contest
    :param contest_hard_end: A `datetime` object representing the hard deadline of the contest
    :param penalty: A penalty score for late submissions
    :param is_public: Field to indicate if the contest is public (or private)
    :param enable_linter_score: Field to indicate if linter scoring is enabled in the contest
    :param enable_poster_score: Field to indicate if poster scoring is enabled in the contest
    :returns: A 2-tuple - 1st element indicating whether the processing has succeeded, and
              2nd element providing an error message if processing is unsuccessful.
    """
    try:
        c = models.Contest(name=contest_name, start_datetime=contest_start,
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
        log_error(str(e))
        return (False, 'Contest could not be created. Cause: {}'.format(str(e)))


def delete_contest(contest_id: int) -> Tuple[bool, Optional[str]]:
    """
    Function to delete a :class:`~judge.models.Contest` given its contest ID.
    This will cascade delete in all the tables that have :attr:`contest_id` as a foreign key.
    It calls :func:`delete_problem` for each problem in the contest.

    :param contest_id: the contest ID
    :returns: A 2-tuple - 1st element indicating whether the deletion has succeeded, and
              2nd element providing an error message if deletion is unsuccessful.
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
        log_error(str(e))
        return (False, 'Contest could not be deleted. Cause: {}'.format(str(e)))


def process_problem(
        contest: int,
        **kwargs: Union[str, int, Optional[InMemoryUploadedFile]]) -> Tuple[bool, Optional[str]]:
    """
    Function to process a new :class:`~judge.models.Problem`.

    :param contest: Contest ID to which the problem belongs

    :attr:`**kwargs` includes the following keyword arguments, which are directly passed
    to the construct a :class:`~judge.models.Problem` object.

    :param code: Problem code
    :type code: str
    :param name: Problem name
    :type name: str
    :param statement: Problem statement
    :type statement: str
    :param input_format: Problem input format
    :type statement: str
    :param output_format: Problem output format
    :type statement: str
    :param difficulty: Problem difficulty
    :type statement: int
    :param time_limit: Problem execution time limit
    :type statement: int
    :param memory_limit: Problem virtual memory limit
    :type statement: int
    :param file_exts: Accepted file format for submissions
    :type statement: str
    :param starting_code: Starting code for the problem
    :type statement: Optional[InMemoryUploadedFile]
    :param max_score: Maximum judge score per test case for the problem
    :type statement: int
    :param compilation_script: Compilation script for the submissions
    :type statement: Optional[InMemoryUploadedFile]
    :param test_script: Test script for the submissions
    :type statement: Optional[InMemoryUploadedFile]
    :returns: A 2-tuple - 1st element indicating whether the processing has succeeded, and
              2nd element providing an error message if processing is unsuccessful.
    """
    # Check if the Problem Code has already been taken
    code = kwargs.get('code')
    try:
        models.Problem.objects.get(pk=code)
        return (False, '{} already a used Question code.'.format(code))
    except models.Problem.DoesNotExist:
        pass

    # Quill replaces empty input with this
    NO_INPUT_QUILL = '{"ops":[{"insert":"\\n"}]}'
    if kwargs.get('statement') == NO_INPUT_QUILL:
        kwargs['statement'] = 'The problem statement is empty.'
    if kwargs.get('input_format') == NO_INPUT_QUILL:
        kwargs['input_format'] = 'No input format specified.'
    if kwargs.get('output_format') == NO_INPUT_QUILL:
        kwargs['output_format'] = 'No output format specified.'

    # if either one of compilation_script or test_script is None,
    # we create a Problem with the default compilation script and/or test_script
    # and then we copy a compilation script and/or test_script to the right location
    # and update the link after creation
    no_comp_script = kwargs.get('compilation_script') is None
    no_test_script = kwargs.get('test_script') is None
    if no_comp_script:
        kwargs['compilation_script'] = './default/compilation_script.sh'
    if no_test_script:
        kwargs['test_script'] = './default/test_script.sh'

    try:
        c = models.Contest.objects.get(pk=contest)
        p = models.Problem.objects.create(contest=c, **kwargs)

        if not os.path.exists(os.path.join('content', 'problems', p.code)):
            # Create the problem directory explictly if not yet created
            # This will happen when both compilation_script and test_script were None
            os.makedirs(os.path.join('content', 'problems', p.code))

        if no_comp_script:
            # Copy the default comp_script if the user did not upload custom
            copyfile(os.path.join('judge', 'default', 'compilation_script.sh'),
                     os.path.join('content', 'problems', p.code, 'compilation_script.sh'))
            p.compilation_script = os.path.join('content', 'problems',
                                                p.code, 'compilation_script.sh')

        if no_test_script:
            # Copy the default test_script if the user did not upload custom
            copyfile(os.path.join('judge', 'default', 'test_script.sh'),
                     os.path.join('content', 'problems', p.code, 'test_script'))
            p.test_script = os.path.join('content', 'problems', p.code, 'test_script')

        # In this case, either one of compilation_script or test_script hasn't been copied
        # and saving with update the link(s)
        if no_comp_script or no_test_script:
            p.save()

        return (True, None)
    except Exception as e:
        print_exc()
        return (False, str(e))


def update_problem(code: str, name: str, statement: str, input_format: str,
                   output_format: str, difficulty: str) -> Tuple[bool, Optional[str]]:
    """
    Function to update selected fields in a :class:`~judge.models.Problem` after creation.
    The fields that can be modified are `name`, `statement`, `input_format`, `output_format`
    and `difficulty`.

    :param code: Problem ID
    :param name: Modified problem name
    :param statement: Modified problem statement
    :param input_format: Modified problem input format
    :param output_format: Modified problem output format
    :param difficulty: Modified problem difficulty
    :returns: A 2-tuple - 1st element indicating whether the update has succeeded, and
              2nd element providing an error message if update is unsuccessful.
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
        return (False, str(e))


def delete_problem(problem_id: str) -> Tuple[bool, Optional[str]]:
    """
    Function to delete a :class:`~judge.models.Problem` given its problem ID.
    This will cascade delete in all the tables that have :attr:`problem_id` as a foreign key.
    It will also delete all the submissions, testcases and related
    directories corresponding to the problem.

    :param problem_id: the problem ID
    :returns: A 2-tuple - 1st element indicating whether the deletion has succeeded, and
              2nd element providing an error message if deletion is unsuccessful.
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
            _check_and_remove(inputfile_path, outputfile_path)

        submissions = models.Submission.objects.filter(problem=problem)
        for submission in submissions:
            submission_path = os.path.join(
                'content', 'submissions',
                'submission_{}{}'.format(submission.pk, submission.file_type))
            _check_and_remove(submission_path)

        rmtree(os.path.join('content', 'problems', problem_id))

        models.Problem.objects.filter(pk=problem_id).delete()
        return (True, None)
    except Exception as e:
        print_exc()
        log_error(str(e))
        return (False, 'Contest could not be deleted. Cause: {}'.format(str(e)))


def process_person(email: str, rank: int = 0) -> Tuple[bool, Optional[str]]:
    """
    Function to process a new :class:`~judge.models.Person`.

    :param email: Email of the person
    :param rank: Rank of the person (defaults to 0).
    :returns: A 2-tuple - 1st element indicating whether the processing has succeeded, and
              2nd element providing an error message if processing is unsuccessful.
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
        return (False, str(e))


def process_testcase(problem_id: str, test_type: str,
                     input_file: InMemoryUploadedFile,
                     output_file: InMemoryUploadedFile) -> Tuple[bool, Optional[str]]:
    """
    Function to process a new :class:`~judge.models.TestCase` for a problem.

    .. warning::
        This function does not rescore all the submissions and so score will not
        change in response to the new testcase. Do not call this function once the
        contest has started, it will lead to erroneous scores.

    :param problem_id: Problem ID to which the testcase is added.
    :param test_type: Type of testcase - one of `public`, `private`.
    :param input_file: Input file for the testcase.
    :param output_file: Output file for the testcase.
    :returns: A 2-tuple - 1st element indicating whether the processing has succeeded, and
              2nd element providing an error message if processing is unsuccessful.
    """
    try:
        problem = models.Problem.objects.get(pk=problem_id)
        t = problem.testcase_set.create(
            public=(test_type == 'public'), inputfile=input_file, outputfile=output_file)
        t.save()
        return (True, None)
    except Exception as e:
        print_exc()
        return (False, str(e))


def delete_testcase(testcase_id: str) -> Tuple[bool, Optional[str]]:
    """
    Function to delete a :class:`~judge.models.TestCase` given its testcase ID.
    This will cascade delete in all the tables where this testcase appears.

    .. warning::
        This function does not rescore all the submissions and so score will not
        change in response to the deleted testcase. Do not call this function once the
        contest has started, it will lead to erroneous scores.

    :param testcase_id: the testcase ID
    :returns: A 2-tuple - 1st element indicating whether the deletion has succeeded, and
              2nd element providing an error message if deletion is unsuccessful.
    """
    try:
        inputfile_path = os.path.join(
            'content', 'testcase', 'inputfile_{}.txt'.format(testcase_id))
        outputfile_path = os.path.join(
            'content', 'testcase', 'outputfile_{}.txt'.format(testcase_id))
        _check_and_remove(inputfile_path, outputfile_path)

        models.TestCase.objects.filter(pk=testcase_id).delete()
        return (True, None)
    except Exception as e:
        print_exc()
        return (False, str(e))


def process_submission(problem_id: str, participant: str, file_type: str,
                       submission_file: InMemoryUploadedFile,
                       timestamp: str) -> Tuple[bool, Optional[str]]:
    """
    Function to process a new :class:`~judge.models.Submission` for a problem by a participant.

    :param problem_id: Problem ID for the problem corresponding to the submission
    :param participant: Participant ID
    :param file_type: Submission file type
    :param submission_file: Submission file
    :param timestamp: Time at submission
    :returns: A 2-tuple - 1st element indicating whether the processing has succeeded, and
              2nd element providing an error message if processing is unsuccessful.
    """
    try:
        problem = models.Problem.objects.get(pk=problem_id)
        if file_type not in problem.file_exts.split(','):
            return (False, 'Accepted file types: \"{}\"'
                           .format(', '.join(problem.file_exts.split(','))))
        participant = models.Person.objects.get(email=participant)
        s = problem.submission_set.create(participant=participant, file_type=file_type,
                                          submission_file=submission_file, timestamp=timestamp)
        s.save()
    except Exception as e:
        print_exc()
        return (False, str(e))

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
        return (False, str(e))

    return (True, None)


def update_poster_score(submission_id: str, new_score: int):
    """
    Function to update the poster score for a submission. Leaderboard is updated if the
    total score for the person-problem pair has changed.

    :param submission_id: Submission ID of the submission
    :param new_score: New score to be assigned
    :returns: A 2-tuple - 1st element indicating whether the update has succeeded, and
              2nd element providing an error message if update is unsuccessful.
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
        return (False, str(e))


def add_person_to_contest(person: str, contest: int,
                          permission: bool) -> Tuple[bool, Optional[str]]:
    """
    Function to relate a person to a contest with permissions.

    :param person: Person ID
    :param contest: Contest ID
    :param permission: If ``True``, then poster, if ``False``, then participant
    :returns: A 2-tuple - 1st element indicating whether the addition has succeeded, and
              2nd element providing an error message if addition is unsuccessful.
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
        return (False, str(e))


def add_person_rgx_to_contest(rgx: str, contest: int,
                              permission: bool) -> Tuple[bool, Optional[str]]:
    """
    Function to relate a set of person to a contest based on a regex with permissions.
    Note that unlike :func:`add_person_to_contest`, this function does not create any new persons.

    :param rgx: The regex to be passed
    :param contest: Contest ID
    :param permission: If ``True``, then poster, if ``False``, then participant
    :returns: A 2-tuple - 1st element indicating whether the relation creation has succeeded, and
              2nd element providing an error message if relation creation is unsuccessful.
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
        return (False, str(e))


def add_persons_to_contest(persons: List[str], contest: int,
                           permission: bool) -> Tuple[bool, Optional[str]]:
    """
    Function to relate a list of persons and contest with permissions. This function
    would create records for all the persons who are not present in the database irrespective
    of whether anyone has conflict or not.

    :param persons: List of person IDs
    :param contest: Contest ID
    :param permission: If ``True``, then poster, if ``False``, then participant
    :returns: A 2-tuple - 1st element indicating whether the relation creation has succeeded, and
              2nd element providing an error message if relation creation is unsuccessful.
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
        return (False, str(e))


def get_personcontest_permission(person: Optional[str], contest: int) -> Optional[bool]:
    """
    Function to give the relation between a :class:`~judge.models.Person` and a
    :class:`~judge.models.Contest`.

    :param person: Person ID
    :param contest: Contest ID
    :returns: If participant, then ``False``, if poster, then ``True``, if neither, then ``None``
    """
    curr = timezone.now()
    if person is None:
        try:
            c = models.Contest.objects.get(pk=contest)
            # The curr >= c.start_datetime is present because contests aren't visible
            # prior to the deadline
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


def delete_personcontest(person: str, contest: int) -> Tuple[bool, Optional[str]]:
    """
    Function to delete the relation between a person and a contest.

    :param person: Person ID
    :param contest: Contest ID
    :returns: A 2-tuple - 1st element indicating whether the deletion has succeeded, and
              2nd element providing an error message if deletion is unsuccessful.
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
        return (False, str(e))


def get_personproblem_permission(person: Optional[str], problem: str) -> Optional[bool]:
    """
    Function to give the relation between a :class:`~judge.models.Person` and a
    :class:`~judge.models.Contest`. This dispatches to :func:`get_personcontest_permission`
    with relevant arguments.

    :param person: Person ID
    :param problem: Problem ID
    :returns: If participant, then ``False``, if poster, then ``True``, if neither, then ``None``
    """
    p = models.Problem.objects.get(pk=problem)
    if p.contest is None:
        return False
    return get_personcontest_permission(person, p.contest.pk)


def get_posters(contest: int) -> Tuple[bool, Union[str, List[str]]]:
    """
    Function to return the list of the posters for a :class:`~judge.models.Contest`.

    :param contest: Contest ID
    :returns: A 2-tuple - 1st element indicating whether the retrieval has succeeded.
              If successful, a list of IDs are present in the 2nd element.
              If unsucessful, an error message is provided.
    """
    try:
        c = models.Contest.objects.get(pk=contest)
        cps = models.ContestPerson.objects.filter(contest=c, role=True)
        cps = [cp.person.email for cp in cps]
        return (True, cps)
    except Exception as e:
        print_exc()
        return (False, str(e))


def get_participants(contest: int) -> Tuple[bool, Union[str, List[str]]]:
    """
    Function to return the list of the participants for a :class:`~judge.models.Contest`.

    :param contest: Contest ID
    :returns: A 2-tuple - 1st element indicating whether the retrieval has succeeded.
              If successful, a list of IDs are present in the 2nd element. The list is
              empty if the contest is public.
              If unsucessful, an error message is provided.
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
        return (False, str(e))


def get_personcontest_score(person: str, contest: int) -> Tuple[bool, Union[float, str]]:
    """
    Function to get the final score, which is the sum of individual final scores
    of all problems in a contest for a particular person.

    :param person: Person ID
    :param contest: Contest ID
    :returns: A 2-tuple - 1st element indicating whether the retrieval has succeeded.
              If successful, the final score is present in the 2nd element.
              If unsuccesful, an error message is provided.
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
        return (False, str(e))


def get_submissions(problem_id: str, person_id: Optional[str]) \
        -> Tuple[bool, Union[Dict[str, List[Any]], str]]:
    """
    Function to retrieve all submissions made by everyone or a specific person for this
    problem.

    :param problem_id: Problem ID
    :param person_id: Person ID
    :returns: A 2-tuple - 1st element indicating whether the retrieval has succeeded.
              If successful, and :attr:`person_id` is ``None``, then the list of submissions
              pertaining to each person is placed in a dictionary, and if :attr:`person_id`
              is provided, then the list of submissions pertaining to the specific person is
              placed in a dictionary and returned.
              If unsuccessful, then an error message is provided.
    """
    try:
        p = models.Problem.objects.get(code=problem_id)
        if person_id is None:
            submission_set = models.Submission.objects.filter(
                problem=p).order_by('participant')
        else:
            person = models.Person.objects.get(email=person_id)
            submission_set = models.Submission.objects.filter(
                problem=p, participant=person)
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
        return (False, str(e))


def get_submission_status(submission: str):
    """
    Function to get the current status of the submission given its submission ID.

    :param submission: Submission ID
    :returns: A 2-tuple - 1st element indicating whether the retrieval has succeeded.
              If successful, a tuple consisting of a dictionary and a smaller tuple.
              The key for the dictionary is the testcase ID, and value is another smaller
              tuple consisting of the verdict, time taken, memory consumed, flag to indicate
              if the testcase was public or private and message after checking.
              The smaller tuple consists of the score given by the judge, poster (if applicable),
              and linter (if applicable), as well as the final score, timestamp of submission and
              the file type of submission.
              If unsuccessful, an error message is provided.
    """
    try:
        s = models.Submission.objects.get(pk=submission)
        testcases = models.TestCase.objects.filter(problem=s.problem)

        verdict_dict = dict()
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
        return (False, str(e))


def get_leaderboard(contest: int) -> Tuple[bool, Union[str, List[List[Union[str, float]]]]]:
    """
    Function to returns the current leaderboard for a contest given its contest ID.

    :param contest: Contest ID
    :returns: A 2-tuple - 1st element indicating whether the retrieval has succeeded.
              If successful, a list of 2-length lists is returned ordered by decreasing
              scores. The first element is the rank, and the second element is the score.
              If unsuccessful, an error message is provided.
    """
    leaderboard_path = os.path.join('content', 'contests', str(contest) + '.lb')
    if not os.path.exists(leaderboard_path):
        return (False, 'Leaderboard not yet initialized for this contest.')
    try:
        with open(leaderboard_path, 'rb') as f:
            data = pickle.load(f)
        return (True, data)
    except Exception as e:
        print_exc()
        return (False, str(e))


def update_leaderboard(contest: int, person: str) -> bool:
    """
    Function to update the leaderboard for a person-contest pair given their IDs.

    .. note::
        Only call this function when some submission for some problem of the contest
        has scored more than its previous submission.
        Remember to call this function whenever
        :class:`~judge.models.PersonProblemFinalScore` is updated.

    :param contest: Contest ID
    :param person: Person ID
    :returns: If update is successful, then ``True``. If unsuccessful, then ``False``.
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
                    timestamp: datetime, comment: str) -> Tuple[bool, Optional[str]]:
    """
    Function to process a new :class:`~judge.models.Comment` on the problem.

    :param problem: Problem ID
    :param person: Person ID
    :param commenter: Commenter (another person) ID
    :param timestamp: Date and Time of comment
    :param comment: Comment content
    :returns: A 2-tuple - 1st element indicating whether the processing has succeeded, and
              2nd element providing an error message if processing is unsuccessful.
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
        return (False, str(e))


def get_comments(problem: str, person: str) -> Tuple[bool, Union[str, List[Tuple[Any]]]]:
    """
    Function to get the private comments on the problem for the person.

    :param problem: Problem ID
    :param person: Person ID
    :returns: A 2-tuple - 1st element indicating whether the retrieval has succeeded.
              If successful, then the 2nd element consists of list of 3-tuple of comments -
              the person who commented, the timestamp and the comment content, sorted in
              chronological order.
              If unsuccessful, an error message is provided.
    """
    try:
        comments = models.Comment.objects.filter(
            problem=problem, person=person).order_by('timestamp')
        result = [(comment.commenter, comment.timestamp, comment.comment)
                  for comment in comments]
        return (True, result)
    except Exception as e:
        print_exc()
        return (False, str(e))


def get_csv(contest: int) -> Tuple[bool, Union[str, StringIO]]:
    """
    Function to get the CSV (in string form) of the current scores of
    all participants in a contest given its contest ID.

    :param contest: Contest ID
    :returns: A 2-tuple - 1st element indicating whether the retrieval has succeeded, and
              2nd element providing an error message if processing is unsuccessful or a
              ``StringIO`` object if successful.
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
        return (False, str(e))
