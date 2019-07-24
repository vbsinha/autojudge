# [autojudge: An Online Judge for Coding contests](https://github.com/vbsinha/autojudge)

[![CircleCI](https://circleci.com/gh/vbsinha/autojudge.svg?style=svg)](https://circleci.com/gh/vbsinha/autojudge) [![Documentation Status](https://readthedocs.org/projects/autojudge/badge/?version=latest)](https://autojudge.readthedocs.io/en/latest/?badge=latest)

---
This is an implementation of an online judge that can be used for conducting programming contests as well as managing assignments in a university.

Apart from the facilities of usual programming contest portals, this portal provides facilities which are well suited for assignment submission.

These additional features include: Instructor (Problem poster) grades above judge scores, soft and hard deadlines for assignments including penalties, customizable compilation and test script, linter scores et cetera.

Currently, the judge supports 5 languages: C, C++, Python, Go and Haskell but this list can be extended easily.

## Requirements

To run this application, you will require **Python 3.6 or above**. While we tested this primarily with Python 3.6 or above, we expect it to work for other Python versions > 3 that support Django 2.2.3.

Other primary requirements are specified in [requirements.txt](requirements.txt). To setup documentation locally, please check the requirements specified in [docs/requirements.txt](docs/requirements.txt).

## Setting up and running the application

The instructions to setup and run this application are specified in our [documentation](https://autojudge.readthedocs.io/en/latest/usage.html).

## Understanding how `autojudge` works

If you are interested in understanding how `autojudge` works, please find the API documentation [here](https://autojudge.readthedocs.io/en/latest/api.html).

## License

This code is licensed under [MIT](LICENSE).
