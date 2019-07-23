User Manual for ``autojudge``
=============================

Some important abstractions / terminology used in ``autojudge``
---------------------------------------------------------------

.. note::
    Please make note of the terms in **bold**

The judge works on graph between **contests** and **users**. A **contest** consists of a set of **problems**. A **user** is, well, a **user** - with different roles.

A user can be either a **poster**, **participant** or neither. A **user** is associated with the **contest** with one and only one role - either a **poster**, **participant** or neither.

The user who creates a new **contest** becomes the **poster** for the **contest** by default.
This user can add more **posters** to help coordinate the **contest** (perhaps by setting new **problems**, verifying and commenting on **submissions**, and so on).

While creating a new **contest**, the first **poster** has an option to either allow select **participants**, or to leave it open for all.
The former kind of a **contest** is a **private contest**, and the latter kind of a **contest** is a **public contest** (for obvious reasons). No **poster** is allowed to take part in a **contest** as a **participant** i.e., he/she cannot submit solutions.

If the **contest** is **public**, every user is either a **poster** or a **participant**. If the **contest** is **private**, a user can either be a **poster**, a **participant** or neither - in which case, he/she will not be permitted to participant in the **contest**.

Maybe a short example will help you understand if something is confusing....

Example:
~~~~~~~~

Take the case of a course assignment with programming questions. These programming questions could compose a **contest**, where each question is a **problem**. The instructor and the TAs can be thought of as the **posters**, while registered students for the course would be **participants**. Students not registered for the course will not be able to participate in this **contest** - as you would expect.

Hands-on with ``autojudge``
---------------------------

Creating your account / Logging in
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You need to be logged in to use ``autojudge``. On the home page, click ``LOG IN`` (see top right corner in the image below)

.. image:: ../_images/log-in.png
   :width: 400
   :align: center
   :alt: Log in screenshot

If this is being used at an institution, please make sure you log in with your institutional account. Currently, we support Google OAuth logins.

Creating a **contest**
----------------------

Once you are logged in, follow the steps below to create a new **contest**.

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

Managing **Problem**
--------------------

A ``Contest`` consists of ``Problem`` s. Only a ``Poster`` can add / edit / delete ``Problem`` s.

1. ``Problem`` can be added only before the start time of the ``Contest``. To add a ``Problem`` click add ``ADD PROBLEM`` from the ``Contest`` page, and fill the form.

    - A unique problem code distinctly identifies a ``Problem``.
    - In case the Compilation Script and Test Script are left empty, the default ones are used. The default scripts can be downloaded from the links just below the Browse buttons.
    - Fill the other feilds appropriately.

2. In the next page, called the ``Problem`` page, add and manage the test-cases. Public test-cases would be visible to the ``Participant`` s while Private ones won't be. Note that test-case addition / deletion will be allowed only till the start of the ``Contest``.
3. A ``Poster`` can edit / delete a ``Problem`` using the 2 buttons on the top-right of the ``Problem`` page. Deletion of a ``Problem`` is only allowed until the ``Contest`` begins.

Managing **Submission** for the **Participant**
-----------------------------------------------

A **participant** can make submission for a **probem** from the problem page. Select the language and upload the submission file.

To check your previous **submissions**, and the judge's score, click the ``SEE MY PREVIOUS SUBMISSIONS`` button at the bottom of the problem page.

To view detailed verdict of the judge, click on the specific submission. Here you can see the verdict of the judge on individual test-cases. You can also download your submission from here.

Once the contest begins and **participants** start scoring, the leaderboard is initialized and can be seen on the **contest** page.
The leaderboard sorts on the basis of the sum of scores in individual **problems** in the contest.

Please note that the ``max score`` seen on the problem page is the max score per test-case, So if there are 5 test-cases and max score is 10 points, then a **participant** can score at most 50 points for that **problem**. 

Managing **Submission** for the **Poster**
------------------------------------------

**Poster** can see all the **submission** pertaining to a **problem** in the **probem** page by clicking on ``SEE ALL SUBMISSIONS`` at the bottom of the page. 
**Submissions** made by all the **participants** for that specific **problem** would be available here. Click on any submission to open the **submission** page to see detailed judge verdict.

In case poster scoring was enabled, the **poster** can give score from the **submission** page by clicking on ``UPDATE POSTER SCORE`` on the top right. Poster score can be positive, negative or zero.

The **poster** can also see the submission file from the **submission** page by clicking on ``DOWNLOAD`` button on the top right.

Commenting
----------

A **poster** or **participant** can also comment. These comments are specific to each **problem** and **participant**.
This is like having private comment between **participant** and **posters** for a specific **problem**.

To see old comments or create a new one, click on ``SEE ALL SUBMISSIONS`` in the problem page.

Miscellaneous
-------------

1. Downloading CSV of all scores: A **poster** can download a CSV file containing the best scores of all **participants** in a **contest** by clicking on ``DOWNLOAD SCORES`` from the **contest** page.

