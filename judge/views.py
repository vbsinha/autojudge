from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import render

from .models import Contest

# Create your views here.


def index(request):
    context = {}
    return render(request, 'judge/index.html', context)

def new_contest(request):
    if request.method == 'POST':
        # TODO
        contest = Contest(name=request.POST['name'], start_date='', end_date='', penalty='')
        contest.save()
        context = {}
        return render(request, 'judge/new_contest.html', context)
    else:
        context = {}
        return render(request, 'judge/new_contest.html', context)
