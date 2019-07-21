User Manual for ``autojudge``
=============================

Creating your account / Logging in
----------------------------------

On the home page, click ``LOG IN`` (see top right corner).
Login via your IITH Google account (OAuth).

Key Abstractions of ``autojudge`` for Users
-------------------------------------------

The judge uses a system of ``Contest`` s.
A ``Contest`` consists of a set of ``Problem`` s.
The list of ``Contest`` s can be seen on the first page after login and is called the dashboard.

A user can be a ``Poster``, a ``Participant`` or neither for a ``Contest``.
For each ``Contest`` a user will hold one and only one position.

The user who creates a ``Contest`` becomes the ``Poster`` for the ``Contest`` by default.
The ``Poster`` can add more ``Poster`` s, who would help in creating the problems, and/or in coordinating the ``Contest``.
These ``Poster`` s together write a set of ``Problem`` s for the ``Contest``, and/or coordinate the ``Contest``.

The ``Poster`` can leave the ``Contest`` open for all users to particpate, in which case it is called a ``Public Contest``. Or the ``Poster`` may specify a set of ``Participant`` s. In this case only these users can particpate in the ``Contest``. Such ``Contest`` s are also called ``Private Contest`` s.
Note that no ``Poster`` can ever participate in a contest.

If the ``Contest`` is ``Public`` every user is either a ``Poster`` or a ``Participant``.
If the ``Contest`` is ``Private``, a user can be either a ``Poster`` or a ``Participant`` or neither. Users who are neither ``Participant`` s nor ``Poster`` s in a ``Private Contest`` will not be allowed to participate in it.

Consider as an example a course assignment. It can be posted as a ``Contest``.
Each individual question becomes a ``Problem``.
The Instructor and the TAs can be ``Poster`` s, while the registered students for that course would be ``Participant`` s.
No other user would be able to participate in that ``Contest``.

Creating a ``Contest``
------------------

1. Click the ``New Contest`` button on the dashboard.
2. Fill out the form for creating the New Contest. 

    - Contest Name distingushes contests and so every contest must have a unique and new name.
    - The ``Soft End Date`` of the ``Contest`` is the date after which all the submissions would incur penalty.
    - The ``Hard End Date`` is the 'deadline' of the assignment; the judge stops accepting submissions after this time.
    - ``Penalty`` is a value between 0 and 1 and specifies the per day penalty on submissions made after Soft End Date.
    - A ``Contest`` having 0.1 penalty for example, would give 90% of the actaully scored points by a submission if it is made within 24 hours of ``Soft End Date`` but before the ``Hard End Date``.
    - It is advised that linter scoring be disabled unless all code submissions are made in Python.
    - Enable ``poster scoring`` if you would like the TA's to give points on top of the ones given by judge.

3. You should be able to see the newly created ``Contest`` on your dashboard. No one else would be able to see this new ``Contest`` on their dashboard until the start time of the ``Contest``.
4. Click on the ``Contest`` in the link on the dashboard to edit it.
5. To add a ``Poster`` to the ``Contest`` click on ``SEE POSTERS``. You can add and delete ``Poster`` s from here. You can add multiple ``Poster`` s by adding their emails in a comma seperated list. The new ``Poster`` s would now be able to see this ``Contest`` on their dashboard (even before the start time). They can also edit the ``Contest``.
6. In case of ``Private Contest`` the ``Poster`` s can also see a ``SEE PARTICIPANTS`` button through which they can edit the ``Participant`` list. Note that trying to add a User both as a ``Participant`` and a ``Poster`` will not be permitted. Avoid editing the ``Poster`` and ``Participant`` list after the ``Contest`` starts.
7. The ``Poster`` can update the dates of the contest from ``UPDATE DATES``. Please update the dates before they actually happen. Updating the ``Soft End date`` and/or ``Hard End Date`` after they have passed would not be allowed.
8. Note that a ``Participant`` cannot add or delete ``Participant`` or ``Poster``. Also (s)he cannot update the dates.

In addition to these a ``Poster`` can delete a ``Contest`` from the button at the bottom of the contest page.

Managing ``Problem``
--------------------

A ``Contest`` consists of ``Problem`` s. Only a ``Poster`` can add / edit / delete ``Problem`` s.

1. ``Problem`` can be added only before the start time of the ``Contest``. To add a ``Problem`` click add ``ADD PROBLEM`` from the ``Contest`` page, and fill the form.

    - A unique problem code distinctly identifies a ``Problem``.
    - In case the Compilation Script and Test Script are left empty, the default ones are used.
    - Fill the other feilds appropriately.

2. In the next page, called the ``Problem`` page, add and manage the test-cases. Public test-cases would be visible to the ``Participant`` s while Private ones won't be. Note that test-case addition / deletion will be allowed only till the start of the ``Contest``.
3. A ``Poster`` can edit / delete a ``Problem`` using the 2 buttons on the top-right of the ``Problem`` page. Deletion of a ``Problem`` is only allowed until the ``Contest`` begins.

Managing ``Submission`` for the ``Participant``
-------------------------------------------

TODO

Managing ``Submission`` for the ``Poster``
--------------------------------------

TODO

Commenting
----------

TODO
