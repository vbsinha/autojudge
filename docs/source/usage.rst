Using ``autojudge``
===================

``autojudge`` is a tool developed for automating evaluation for code submission in coding contests and in assigments at college. For your convenience, we have split this usage manual into 3 phases.

Phase 1 : Get ``autojudge`` and set up your environment
-------------------------------------------------------

Phase 1a: Getting ``autojudge``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``autojudge`` is available on GitHub, and you can download a version of your choice from the `releases page <https://github.com/vbsinha/autojudge/releases>`_. We prefer that you use the latest version.

Extract the compressed files and you now have ``autojudge`` ready to use.

If you are a fan of ``master``, then clone the repository, either using ``git`` or by downloading from GitHub from `here <https://github.com/vbsinha/autojudge>`_.

Phase 1b: Setting up your environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The evaluation of submissions are conducted on a Docker image that is built while initializing the application. Please install Docker using the instructions provided on `their installation page <https://docs.docker.com/install/linux/docker-ce/ubuntu>`_.

If you are very conservative about populating your default environment with random Python packages, create a virtual environment for installing some *new* packages either using ``virtualenv`` or ``conda-env``.

Install the requirements specified in `requirements.txt <../../../requirements.txt>`_. Don't forget to activate your environment if you have one.
