================================================================================
Welcome to Starter
================================================================================

**Note: This code is part of a collection of various starter examples. See more
at: https://github.com/seedifferently/starters**

This is an opinionated Python web application. It utilizes a "full-stack" Python
web development framework comprised of the following packages:

Pyramid_
    A small, fast, down-to-earth Python web framework.

SQLAlchemy_
    A SQL toolkit and Object Relational Mapper that gives application developers
    the full power and flexibility of SQL.

Jinja2_
    A modern and designer-friendly templating language.

FormEncode_
    A validation and form generation package.

WebHelpers2_
    A library of helper functions intended to make writing web applications
    easier.


.. _Pyramid: http://docs.pylonsproject.org/projects/pyramid/en/latest/
.. _SQLAlchemy: http://docs.sqlalchemy.org/en/latest/
.. _Jinja2: http://jinja.pocoo.org/docs/
.. _FormEncode: http://www.formencode.org/en/latest/
.. _WebHelpers2: http://webhelpers2.readthedocs.org/en/latest/


--------------------------------------------------------------------------------
Getting Started
--------------------------------------------------------------------------------

Environment Setup
^^^^^^^^^^^^^^^^^

It is highly recommended that you use a Python environment manager such as
pyenv_ or virtualenvwrapper_ to manage your Python development environment.


.. _pyenv: http://github.com/yyuu/pyenv#installation
.. _virtualenvwrapper: http://virtualenvwrapper.readthedocs.org/


Project Initialization
^^^^^^^^^^^^^^^^^^^^^^

Once you have correctly set up and activated your Python environment, you can
initialize the project and its dependencies by running this command in the
project's root directory::

    python setup.py develop


.. note:: If you are using ``pyenv`` to manage your Python environment
          (recommended), you may need to subsequently run ``pyenv rehash``.


Database Initialization
^^^^^^^^^^^^^^^^^^^^^^^

Before starting the app, you'll want to execute the database initialization
script by running::

    initialize_starter_db development.ini


--------------------------------------------------------------------------------
Running the App
--------------------------------------------------------------------------------

You can start the application with Pyramid's ``pserve`` command, specifying
the ``<environment>.ini`` configuration that you would like it to load.

In the root directory of the project, simply run::

    pserve development.ini

You may also want to specify the ``--reload`` option to monitor for changes, or
the ``--daemon`` option to run in daemon (background) mode. Type ``pserve -h``
for more information.


Interactive Shell
^^^^^^^^^^^^^^^^^

Pyramid's `interactive shell`_ can be run using the ``pshell`` command, and will
take advantage of IPython's enhancements if you have IPython_ installed::

    pip install ipython
    pshell development.ini

The Starter project provides shortcut access to its models via the ``m`` object
within the interactive shell, e.g.::

    >>> user = m.User.first()
    >>> user.email
    user@example.com
    >>> m.User.all()
    [<User: user@example.com>,
     <User: superuser@example.com>,
     <User: admin@example.com>,
     <User: testing@example.com>]

.. _interactive shell: http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/commandline.html#the-interactive-shell
.. _IPython: http://ipython.org/


--------------------------------------------------------------------------------
Testing
--------------------------------------------------------------------------------

The application's test suite can be found in the ``tests`` directory. It is
broken into three parts:

:functional:
    Functional tests use the WebTest_ package to test the application in its
    "fully-loaded" state. These tests run and check pieces of the application as
    if it were being accessed by a user with a web browser.

:model:
    Model tests relate to the application's model classes.

:unit:
    The ``unit`` test directory is meant for tests that don't necessarily fit
    into the other two categories (e.g. for testing helpers or other small
    "units" of code).


.. _WebTest: http://webtest.readthedocs.org/


Running the Tests
^^^^^^^^^^^^^^^^^

You can run the tests by typing::

    python setup.py test

This will run the full test suite in basic output mode. For more advanced
testing, see the next section about nose.


Testing with nose
^^^^^^^^^^^^^^^^^

nose_ is a package which extends Python's basic testing functionality in various
ways.

To run nose, first make sure the full testing dependencies have been met by
running::

    pip install -e .[tests]

Once the install has finished, you can run nose by typing::

    nosetests

With nose, you can also "focus" on individual tests by referencing them via
their "dotted Python name" with nose's ``--tests`` option.

For example, the following would only run the "test_index" test from the
"TestRoot" functional test class::

    nosetests --tests starter.tests.functional.test_root:TestRoot.test_index

Type ``nosetests -h`` for more options.


.. _nose: http://nose.readthedocs.org/


--------------------------------------------------------------------------------
Documentation
--------------------------------------------------------------------------------

The application's documentation can be found in the ``docs`` directory. The
docs are written in reStructuredText_ and use Sphinx_ for documentation
generation.


.. _reStructuredText: http://sphinx-doc.org/rest.html
.. _Sphinx: http://sphinx-doc.org/


Building the Docs
^^^^^^^^^^^^^^^^^

First make sure the full documentation dependencies have been met by running::

    pip install -e .[docs]

Then you'll need to initialize the git submodule containing the documentation's
output theme by running::

    git submodule init
    git submodule update

Next, ``cd`` into the ``docs`` directory and run::

    make html

You should now be able to browse the full documentation by opening
``./docs/_build/html/index.html`` in your web browser.


.. include:: starter.rst
