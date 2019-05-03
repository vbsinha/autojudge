# [PDP: Programming and Discussion Portal](https://github.com/vbsinha/pdp-judge)

[![CircleCI](https://circleci.com/gh/vbsinha/pdp-judge.svg?style=svg&circle-token=779cf1772a65883845be7ded61285e17a63141de)](https://circleci.com/gh/vbsinha/pdp-judge)

---
This is an implementation of an online judge. 
The portal can be used for conducting programming contests as well as managing assignments in a university.
Apart from the facilities of a usual programming contest portals, this portal provides facilities which are well suited for assignment submission. 
These additional features include: Instructor (Problem poster) grades above judge scores, soft and hard deadlines for assignments including penalties, customizable compilation and test script, linter scores etc.

## Prerequisites

The prerequisites are:
* Python 3.7
* Django 2.2
* social-auth-app-django (Install using ```pip install social-auth-app-django```)

## Running the program

* Clone this repo
* Go to the directory and run
```
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py runserver
```
* Also run the submission_watcher_saver program. 
This program runs the submissions on testcases and produces output. 
It must always be kept throughout the time server is running.
```
$ python submission_watcher_saver.py
```
