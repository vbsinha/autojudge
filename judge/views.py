from django.shortcuts import render, redirect, get_object_or_404
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
import logging

from .models import Contest, Problem, TestCase
from .forms import NewContestForm
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
            # TODO Filter the private contests only foe which he is poster/participant
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
            print('Form is valid')
            contest_name = form.cleaned_data['contest_name']
            contest_start = form.cleaned_data['contest_start']
            contest_end = form.cleaned_data['contest_end']
            # TODO validate penalty b/w 0 and 1
            penalty = form.cleaned_data['penalty']
            is_public = form.cleaned_data['is_public']

            status, msg = handler.process_contest(
                contest_name, contest_start, contest_end, penalty, is_public)
            if status:
                return redirect('/judge/')
            else:
                logging.debug(msg)
                form.add_error(None, 'Contest could not be created.')
    else:
        form = NewContestForm()
    context = {'form': form}
    return render(request, 'judge/new_contest.html', context)


def add_poster(request, contest_id, permission=True):
    # TODO Error handling
    if request.method == 'POST':
        status, err = handler.add_person_to_contest(
            request.POST.get('email'), contest_id, permission)
        if status:
            return redirect(request.META['HTTP_REFERER'])
    return redirect(request.META['HTTP_REFERER'])


def add_participant(request, contest_id):
    return add_poster(request, contest_id, False)


def contest_detail(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    problems = Problem.objects.filter(contest_id=contest_id)
    return render(request, 'judge/contest_detail.html', {
        'contest': contest,
        'problems': problems,
        'contest_start': contest.start_datetime.strftime('%d-%m-%Y %H:%M'),
        'contest_end': contest.end_datetime.strftime('%d-%m-%Y %H:%M'),
    })


def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, pk=problem_id)
    return render(request, 'judge/problem_detail.html', {
        'problem': problem,
        'public_tests': TestCase.objects.filter(problem_id=problem_id, public=True),
        'private_tests': TestCase.objects.filter(problem_id=problem_id, public=False),
    })


def new_problem(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    if request.method == 'POST':
        # TODO Sanitize input
        # Ensure that time_limit is not null (For int conversion)
        status, err = handler.process_problem(request.POST.get('code'),
                                              contest_id,
                                              request.POST.get('name'),
                                              request.POST.get('statement'),
                                              request.POST.get('input_format'),
                                              request.POST.get(
                                                  'output_format'),
                                              request.POST.get('difficulty'),
                                              timedelta(milliseconds=int(
                                                  request.POST.get('time_limit'))),
                                              request.POST.get('memory_limit'),
                                              request.POST.get('file_format'),
                                              request.FILES.get('start_code'),
                                              request.POST.get('max_score'),
                                              request.FILES.get(
                                                  'compilation_script'),
                                              request.FILES.get('test_script'),
                                              request.FILES.get(
                                                  'setter_solution'))
        print(request.POST)
        if status:
            # no_test_cases = int(request.POST['no_test_cases'])
            # print(no_test_cases)
            # for i in range(no_test_cases):
            #     status, err = handler.process_testcase(
            #         request.POST['code'], True if request.POST['test'+str(i)] == 'on' else False,
            #         request.FILES.get('input'+str(i)), request.FILES.get('output'+str(i)))
            #     print(status, err)
            return redirect('/judge/contest/{}/'.format(contest_id))
        else:
            print(err)
            context = {'error_msg': 'Could not create new problem',
                       'post_data': request.POST,
                       'contest': contest}
            return render(request, 'judge/new_problem.html', context)
    else:
        context = {'contest': contest}
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
