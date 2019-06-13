Using ``autojudge``
===================

``autojudge`` is a tool developed for automating evaluation for code submission in coding contests and in assigments at college. For your convenience, we have split this usage manual into 3 phases.

Phase 1 : Get ``autojudge`` and set up your environment
-------------------------------------------------------

Phase 1a: Getting ``autojudge``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``autojudge`` is available on GitHub, and you can download a version of your choice from the `releases page <https://github.com/vbsinha/autojudge/releases>`_. We prefer that you use the latest version.

Extract the compressed files and you now have ``autojudge`` ready to use.

If you are a fan of ``master``, then clone the repository, either using ``git`` or by downloading from GitHub from `here <https://github.com/vbsinha/autojudge>`__.

Phase 1b: Setting up your environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The evaluation of submissions are conducted on a Docker image that is built while initializing the application. Please install Docker using the instructions provided on `their installation page <https://docs.docker.com/install/linux/docker-ce/ubuntu>`__.

If you are very conservative about populating your default environment with random Python packages, create a virtual environment for installing some *new* packages either using ``virtualenv`` or ``conda-env``.

Install the requirements specified in |requirements.txt|_. Don't forget to activate your environment if you have one.

.. |requirements.txt| replace:: ``requirements.txt``
.. _requirements.txt: ../../../requirements.txt

If you going to deploy ``autojudge``, please install PostgreSQL using the instructions provided on `their installation page <https://www.postgresql.org/download/linux/ubuntu/>`__.

Phase 2 : Run ``autojudge``
---------------------------

Activate your environment.

Create and apply database migrations in Django with the following commands:

.. code:: bash

    python manage.py makemigrations
    python manage.py migrate

There are two ways of using ``autojudge``.

Development
~~~~~~~~~~~

To run ``autojudge`` locally:

.. code:: bash

    python manage.py runserver

Go to ``localhost:8000`` in your favourite browser. Keep yourself connected to internet for full functionality as certain frontend support such as JavaScript scripts are pulled from the internet.

The program |submission_watcher_saver.py|_ scores the submissions serially in the chronological order of submissions. It can be started anytime after the server has started, but it is preferred that the program be kept running in parallel with the server. Run it using:

.. |submission_watcher_saver.py| replace:: ``submission_watcher_saver.py``
.. _submission_watcher_saver.py: ../../../submission_watcher_saver.py

.. code:: bash

    python submission_watcher_saver.py


Production
~~~~~~~~~~

The procedure to deploy ``autojudge`` is different from running locally. Below are a series of steps that will help you deploy ``autojudge``.

Set the environmental variable ``AUTOJUDGE_SECRET_KEY`` to a random string, which should not be exposed to anyone. Think of it to be a private key.

Now modify a few more settings to |settings_production.py|_. The first is to setup the database. We suggest using a PostgreSQL database. This modification can be done by adding the below dictionary to |settings_production.py|_. Modify the values ``NAME``, ``USER``, ``PASSWORD``, ``HOST`` and ``PORT`` accordingly.

.. code:: python

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'mydatabase',  # Sample
            'USER': 'mydatabaseuser',  # Sample
            'PASSWORD': 'mypassword',  # Sample
            'HOST': '127.0.0.1',  # Sample
            'PORT': '5432',  # Sample
        }
    }


Next we setup the ``STATIC_ROOT`` path, the location where you would like the static files to be generated. This has to be set in |settings_production.py|_.

To generate the static files, run:

.. code:: bash

    python manage.py collectstatic --settings=autojudge.settings_production.py

The static files are generated in the path specified by ``STATIC_ROOT`` previously. 

Now host the static files on a server and configure the URL in ``STATIC_URL`` in |settings_production.py|_. If you have hosted the generated static files at https://static.autojudge.com, then change the ``STATIC_URL`` to https://static.autojudge.com/ (note the trailing slash is required).

You could optionally setup a cache server. Instructions to do this are specified `here <https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-CACHES>`__.

Configure the security settings in |settings_production.py|_ (leave it to the default values if you will be hosting on ``https``).

.. |settings_production.py| replace:: ``settings_production.py``
.. _settings_production.py: ../../../autojudge/settings_production.py

To configure the Apache server using ``WSGI``, follow the instructions `here <https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/>`__.

And finally, set environment variable ``DJANGO_SETTINGS_MODULE`` to ``autojudge.settings_production`` as opposed to ``autojudge.settings`` which is present by default.
