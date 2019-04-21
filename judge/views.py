from django.shortcuts import render, redirect, get_object_or_404
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
import logging

from .models import Contest, Problem, TestCase
from .forms import NewContestForm, AddPersonToContestForm, DeletePersonFromContest, NewProblemForm
from . import handler


def _get_user(request) -> User:
    if request.user.is_authenticated:
        return request.user
    else:
        return None


def handler404(request):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)


def index(request):
    context = {}
    user = _get_user(request)
    if user is not None:
        status, err = handler.process_person(request.user.email)
        if status:
            contests = Contest.objects.all()
            permissions = [handler.get_personcontest_permission(
                user.email, contest.pk) for contest in contests]
            context['contests'] = zip(contests, permissions)
            return render(request, 'judge/index.html', context)
        else:
            logging.debug(
                'Although user is not none, it could not be processed. More info: {}'.format(err))
    contests = Contest.objects.filter(public=True)
    context['contests'] = zip(contests, [False] * len(contests))
    return render(request, 'judge/index.html', context)


def new_contest(request):
    user = _get_user(request)
    if user is None:
        return handler404(request)
    if request.method == 'POST':
        form = NewContestForm(request.POST)
        if form.is_valid():
            contest_name = form.cleaned_data['contest_name']
            contest_start = form.cleaned_data['contest_start']
            contest_end = form.cleaned_data['contest_end']
            penalty = form.cleaned_data['penalty']
            is_public = form.cleaned_data['is_public']
            if penalty < 0 or penalty > 1:
                form.add_error('penalty', 'Penalty should be between 0 and 1.')
            else:
                status, msg = handler.process_contest(
                    contest_name, contest_start, contest_end, penalty, is_public)
                if status:
                    handler.add_person_to_contest(user.email, msg, True)
                    return redirect('/judge/')
                else:
                    logging.debug(msg)
                    form.add_error(None, 'Contest could not be created.')
    else:
        form = NewContestForm()
    context = {'form': form}
    return render(request, 'judge/new_contest.html', context)


def get_posters(request, contest_id, role=True):
    contest = get_object_or_404(Contest, pk=contest_id)
    user = _get_user(request)
    perm = handler.get_personcontest_permission(
        None if user is None else user.email, contest_id)
    if perm is None:
        return handler404(request)
    if role is None:
        return handler404(request)
    contest = get_object_or_404(Contest, pk=contest_id)
    if user is None or (not role and contest.public):
        return handler404(request)
    context = {'contest_id': contest_id,
               'type': 'Poster' if role else 'Participant'}
    if request.method == 'POST':
        form = DeletePersonFromContest(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            status, err = handler.delete_personcontest(email, contest_id)
            if not status:
                logging.debug(err)
                form.add_error(None, 'Could not delete {}.'.format(email))
    else:
        form = DeletePersonFromContest()
    context['form'] = form
    if role:
        status, value = handler.get_posters(contest_id)
    else:
        status, value = handler.get_participants(contest_id)
    if status:
        context['persons'] = value
    else:
        return handler404(request)
    return render(request, 'judge/contest_persons.html', context)


def get_participants(request, contest_id):
    return get_posters(request, contest_id, False)


def add_poster(request, contest_id, role=True):
    # TODO Have comma seperated values
    user = _get_user(request)
    perm = handler.get_personcontest_permission(
        None if user is None else user.email, contest_id)
    if not (perm is True):
        return handler404(request)
    context = {'contest_id': contest_id,
               'type': 'Poster' if role else 'Participant'}
    if request.method == 'POST':
        form = AddPersonToContestForm(request.POST)
        if form.is_valid():
            status, err = handler.add_person_to_contest(
                request.POST.get('email'), contest_id, role)
            if status:
                return redirect('/judge/contest/{}/{}s/'.format(
                    contest_id, context['type'].lower()))
            else:
                form.non_field_errors = err
    else:
        form = AddPersonToContestForm()
    context['form'] = form
    return render(request, 'judge/contest_add_person.html', context)


def add_participant(request, contest_id):
    return add_poster(request, contest_id, False)


def contest_detail(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    user = _get_user(request)
    perm = handler.get_personcontest_permission(
        None if user is None else user.email, contest_id)
    if perm is None:
        return handler404(request)
    problems = Problem.objects.filter(contest_id=contest_id)
    return render(request, 'judge/contest_detail.html', {
        'contest': contest,
        'type': 'Poster' if perm else 'Participant',
        'problems': problems,
        'contest_start': contest.start_datetime.strftime('%d-%m-%Y %H:%M'),
        'contest_end': contest.end_datetime.strftime('%d-%m-%Y %H:%M'),
    })


def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, pk=problem_id)
    user = _get_user(request)
    perm = handler.get_personcontest_permission(
        None if user is None else user.email, problem.contest.pk)
    if perm is None:
        return handler404(request)
    return render(request, 'judge/problem_detail.html', {
        'problem': problem,
        'type': 'Poster' if perm else 'Participant',
        'public_tests': TestCase.objects.filter(problem_id=problem_id, public=True),
        'private_tests': TestCase.objects.filter(problem_id=problem_id, public=False),
    })


def new_problem(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    user = _get_user(request)
    perm = handler.get_personcontest_permission(
        None if user is None else user.email, contest_id)
    if not (perm is True):
        return handler404(request)
    context = {'contest': contest}
    if request.method == 'POST':
        form = NewProblemForm(request.POST, request.FILES)
        if form.is_valid():
            code = form.cleaned_data['code']
            status, err = handler.process_problem(
                code, contest_id, form.cleaned_data['name'], form.cleaned_data['statement'],
                form.cleaned_data['input_format'],
                form.cleaned_data['output_format'], form.cleaned_data['difficulty'],
                form.cleaned_data['time_limit'], form.cleaned_data['memory_limit'],
                form.cleaned_data['file_exts'], form.cleaned_data['starting_code'],
                form.cleaned_data['max_score'], form.cleaned_data['compilation_script'],
                form.cleaned_data['testing_script'], form.cleaned_data['setter_soln'])
            if status:
                return redirect('/judge/problem/{}/'.format(code))
            else:
                form.add_error(None, err)
    else:
        form = NewProblemForm()
    context['form'] = form
    return render(request, 'judge/new_problem.html', context)


def add_test_case_problem(request, problem_id):
    if request.method == 'POST':
        status, err = handler.process_testcase(problem_id,
                                               True if request.POST.get(
                                                   'test-type') == 'public' else False,
                                               request.FILES.get('input'),
                                               request.FILES.get('output'))
        print(status, err)
        if status:
            return redirect(request.META['HTTP_REFERER'])
        else:
            print(err)
            return redirect(request.META['HTTP_REFERER'])
    else:
        print('Not POST')
        return redirect(request.META['HTTP_REFERER'])


def edit_problem(request, problem_id):
    problem = get_object_or_404(Problem, pk=problem_id)
    contest = get_object_or_404(Contest, pk=problem.contest_id)
    # TODO
    pass


def problem_submit(request, problem_id):
    if request.method == 'POST':
        # TODO What is file_type?
        # TODO Process return and display result
        status, err = handler.process_solution(
            problem_id, request.user.email, '.cpp', request.FILES.get('file'), timezone.now())
        if status:
            # TODO give status
            return redirect('/judge/')
        else:
            print(err)
            return redirect(request.META['HTTP_REFERER'])
    else:
        return redirect('/judge/')
