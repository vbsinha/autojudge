from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from datetime import timedelta

from .models import Contest
from . import handler

# Create your views here.


def index(request):
    context = {}
    return render(request, 'judge/index.html', context)


def new_contest(request):
    if request.method == 'POST':
        # TODO Sanitize input
        if handler.process_contest(request.POST['name'], request.POST['start_date'] + '+0530', request.POST['end_date'] + '+0530', request.POST['penalty']):
            return redirect('/judge/')
        context = {'error_msg': 'Could not create new contest',
                   'post_data': request.POST}
        return render(request, 'judge/new_contest.html', context)
    else:
        context = {}
        return render(request, 'judge/new_contest.html', context)


def contest_detail(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    return render(request, 'judge/contest_detail.html', {
        'contest': contest,
        'contest_start': contest.start_datetime.strftime('%d-%m-%Y %H:%M'),
        'contest_end': contest.end_datetime.strftime('%d-%m-%Y %H:%M'),
    })


def new_problem(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    if request.method == 'POST':
        # TODO Sanitize input
        if handler.process_problem(request.POST['code'], request.POST['name'], request.POST['statement'], request.POST['input_format'], request.POST['output_format'],
                                   request.POST['difficulty'], timedelta(milliseconds=int(
                                       request.POST['time_limit'])), request.POST['memory_limit'], request.POST['file_format'],
                                   request.FILES['start_code'], request.POST['max_score'], None if 'comp_script' not in request.FILES else request.FILES['comp_script'], None if 'test_script' not in request.FILES else request.FILES['test_script'], None if 'setter_solution' not in request.FILES else request.FILES['setter_solution']):
            return redirect('/judge/contest/{}/'.format(contest_id))
        else:
            context = {'error_msg': 'Could not create new problem',
                       'post_data': request.POST, 'contest': contest}
            return render(request, 'judge/new_problem.html', context)
    else:
        context = {'contest': contest}
        return render(request, 'judge/new_problem.html', context)
