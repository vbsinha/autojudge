Models and Database Schema
==========================

.. automodule:: judge.models

Base Models
-----------

Contest
~~~~~~~
    .. autoclass:: Contest
        :members:
        :exclude-members: DoesNotExist, MultipleObjectsReturned

Problem
~~~~~~~~~
    .. autoclass:: Problem
        :members:
        :exclude-members: DoesNotExist, MultipleObjectsReturned

Submission
~~~~~~~~~~
    .. autoclass:: Submission
        :members:
        :exclude-members: DoesNotExist, MultipleObjectsReturned

TestCase
~~~~~~~~
    .. autoclass:: TestCase
        :members:
        :exclude-members: DoesNotExist, MultipleObjectsReturned

Person
~~~~~~
    .. autoclass:: Person
        :members:
        :exclude-members: DoesNotExist, MultipleObjectsReturned

Comment
~~~~~~~
    .. autoclass:: Comment
        :members:
        :exclude-members: DoesNotExist, MultipleObjectsReturned

Derived Models
--------------

ContestPerson
~~~~~~~~~~~~~
    .. autoclass:: ContestPerson
        :members:
        :exclude-members: DoesNotExist, MultipleObjectsReturned

SubmissionTestCase
~~~~~~~~~~~~~~~~~~
    .. autoclass:: SubmissionTestCase
        :members:
        :exclude-members: DoesNotExist, MultipleObjectsReturned

PersonProblemFinalScore
~~~~~~~~~~~~~~~~~~~~~~~
    .. autoclass:: PersonProblemFinalScore
        :members:
        :exclude-members: DoesNotExist, MultipleObjectsReturned
