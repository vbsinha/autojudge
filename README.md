# [autojudge: An Online Judge for Coding contests](https://github.com/vbsinha/autojudge)

[![CircleCI](https://circleci.com/gh/vbsinha/autojudge.svg?style=svg)](https://circleci.com/gh/vbsinha/autojudge)

---
This is an implementation of an online judge that can be used for conducting programming contests as well as managing assignments in a university.

Apart from the facilities of usual programming contest portals, this portal provides facilities which are well suited for assignment submission.

These additional features include: Instructor (Problem poster) grades above judge scores, soft and hard deadlines for assignments including penalties, customizable compilation and test script, linter scores et cetera.

Currently, the judge supports 3 languages: C, C++, Python, but this list can be extended easily.

## Pre-requisites

To run this application, you will require **Python 3.6 or above**. While we tested this primarily with Python 3.6 or above, we expect it to work for other Python versions > 3.

We have used **Django 2.2** to build this application. Additionally, we use **social-auth-app-django** for authentication purposes. **Docker** is used to run and evaluate submissions.

## Running the application

- Open a terminal instance and clone the repository using:
```bash
git clone https://github.com/vbsinha/autojudge
```

- Enter the folder by:
```bash
cd autojudge/
````

- Create and apply database migrations in Django with the following commands:
```bash
python manage.py makemigrations
python manage.py migrate
```

- To run the server locally, enter:
```bash
python manage.py runserver
```

- Open the application on your browser at `localhost:8000`.
  - Please note that certain elements of the application require a working internet connection. It is recommended that this application is used with a working internet connection for this reason.

- Run the `submission_watcher_saver.py` program using `python submission_watcher_saver.py`. This program is responsible for running and scoring the submissions on the Docker image. This program can be started at any time after the server has started, but it is preferred that the program be kept running in parallel with the server.

## License

This code is licensed under [MIT](LICENSE).
