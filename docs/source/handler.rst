Handlers and database management
================================

.. automodule:: judge.handler

Process Functions
-----------------

    .. autofunction:: process_contest
    .. autofunction:: process_problem
    .. autofunction:: process_submission
    .. autofunction:: process_testcase
    .. autofunction:: process_person
    .. autofunction:: process_comment

Addition Functions
------------------

    .. autofunction:: add_person_to_contest
    .. autofunction:: add_person_rgx_to_contest
    .. autofunction:: add_persons_to_contest

Update Functions
----------------

    .. autofunction:: update_problem
    .. autofunction:: update_poster_score
    .. autofunction:: update_leaderboard

Getter Functions
----------------

    .. autofunction:: get_personcontest_permission
    .. autofunction:: get_personproblem_permission
    .. autofunction:: get_posters
    .. autofunction:: get_participants
    .. autofunction:: get_personcontest_score
    .. autofunction:: get_submission_status
    .. autofunction:: get_submissions
    .. autofunction:: get_leaderboard
    .. autofunction:: get_comments
    .. autofunction:: get_csv

Deletion Functions
------------------

    .. autofunction:: delete_contest
    .. autofunction:: delete_problem
    .. autofunction:: delete_testcase
    .. autofunction:: delete_personcontest
