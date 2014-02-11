:title: Settei
:date: 2014-01-29 12:03
:summary: Settings config system based on entry points of setuptools
:category: Open source
:author: Spyros Ioakeimidis
:slug: articles/settei
:tags: open source, python, settings, entry points, setuptools

Settei is a generic purpose python settings library based on the concept of
entry points as a registry, inspired by `setuptools <http://pythonhosted.org/setuptools/pkg_resources.html#entry-points>`_.

.. contents::

Introduction
############

:code:`settei` is a generic purpose python settings library which uses entry
points as a registry. It is a library which provides the possibility to define
and use configuration settings from entry points for specific application and
environment. :code:`settei` introduces two terms, **environment** and **application**.

* **environment** is the name of an entry point
* **application** is part of a group's name in which environments are defined

Motivation
##########

Introducing a new environment should be easy and without too much hassle. We
should have possibility to inherit/extend settings from other settings.

Exclude templates for generating settings because it is really hard to read
templates with tons of expressions.

Storing settings separately from our application, scripts (it is good for
storing secret settings that makes them more safely)


Design
######

Entry points
============

Entry points provide an intuitive way for distributions to expose Python objects,
such as functions or classes, to be used by other distributions. Applications
can then search for specific entry points. :code:`settei` uses the concept of
entry points to define groups of environments.

It means that we will have the possibility to store settings in distribution.
Then if we want to get access to settings of live or staging, we will need to
have access install to this distribution and include this distribution in sys.path
of the script or application.

Groups and environments
-----------------------

A group is a container of environments. A group name comprises of two parts.
The first of them is a standard prefix part :code:`settings_`, and the second
one is the name of an application. For example, :code:`settings_application1` or
:code:`settings_application2`, where :code:`application1` and :code:`application2`
are the name of the applications. The prefix part in the group name is important
as it helps to identify only entry points useful for :code:`settei` and iterate
through them.

Each environment name inside a group must be unique. For example, if we have a
group :code:`settings_application1` there should only be one environment named
:code:`default` and only one named :code:`local`. If we specify environments
with the same name inside a group, then a :code:`DuplicateEntryPoint` exception
will be raised. However, we can specify same environment names that belong to
different groups.

Example Usage
#############

:code:`settei` package is easy on its use. The best way to explain how
:code:`settei` can be used is through examples. At first, we need to define
groups and environments. Then, we can create settings for each defined
environment and use them accordingly in the rest of the application.

Define groups and environments
==============================

As a first step, we need to define environments and put them into groups.

.. code-block:: python

    # in the setup.py
    setup (
        # ...
        entry_points = {
            'settings_application1': [
                'default = path.to.package.of.application1.default_settings:generate_config',
                'local = path.to.package.of.application1.local_settings:generate_config',
            ],
            'settings_application2': [
                'default = path.to.package.of.application2.default_settings:generate_config',
                'local = path.to.package.of.application2.local_settings:generate_config',
            ]
        }
        # ...
    )

Create settings
===============

Settings should be created in the :code:`generate_config` function. The :code:`generate_config`
function should return an instance of :code:`settei.config.Config` class.
Settings can be created either directly, read them from a python file, or from
an object. If there is any error during configuration or a :code:`settei.config.Config`
instance is not returned, then a :code:`WrongConfigTypeError` exception is raised.

.. code-block:: python

    # application/default_settings.py
    from settei.config import Config

    def generate_config():
        config = Config()

        # create settings directly
        config['QUESTION'] = 'The Ultimate Question of Life, the Universe, and Everything'
        config['ANSWER'] = 41

        # or load them from a file
        config.from_pyfile('full/path/to/file.py')

        # or from an object
        config.from_object('path.to.object')

        return config

Read settings
=============

After :code:`settei` package is installed, we can use it to get config settings
for the groups that we have already defined. Note that in :code:`get_config`
function we specify the application name and not the group name. For example,
if we want to load settings for the application :code:`application1` and we have
defined a group of environments with the name :code:`settings_application1`,
then in the :code:`get_config` function we just use the name of the application,
which in this case is :code:`application1`.

.. code-block:: python

    from settei import get_config

    # get config settings for 'applicaion1' application and 'local' environment
    config = get_config('application1', 'local')

    # get config settings for 'application2' application and 'local' environment
    config = get_config('application2', 'local')

    # now you can use it as you want
    DEBUG = config['DEBUG']

If the environment from which we want to read settings does not exist, then a
:code:`EnvironmentNotSpecified` exception is raised. Another way to define the
desired environment is using the :code:`CONFIG_ENVIRONMENT` variable.

.. code-block:: python

    # run script/application in this way
    $ ENV CONFIG_ENVIRONMENT='dev' python my_incredible_script.py

Then, in ``my_incredible_script.py`` when the :code:`get_config` function is
used, we do not need to specify an environment as it will use the :code:`dev`
environment that is defined by :code:`CONFIG_ENVIRONMENT`.

.. code-block:: python

    # and in my_incredible_script.py we can use get_config
    from settei import get_config

    # get config settings for 'application1' application and 'dev' environment,
    # which has been specified when running my_incredible_script.py
    config = get_config('application1')

Settings inheritance
====================

Settings can also inherit other settings. However, this is only possible
for settings that belong to the same group of environments. For instance, if
you want your :code:`local` settings to inherit from :code:`default` settings,
then in the :code:`generate_config` function you should mention the name of
environment from which you want to inherit.

.. code-block:: python

    # in your application/local_settings.py file
    # 'default' is the environment from which we want to inherit settings
    def generate_config(default):

        # change a setting, the right answer is 42
        default['ANSWER'] = 42

        return default

If we read the :code:`local` settings, then we will see that
:code:`config['ANSWER']` setting returns the value defined in
:code:`local_settings.py`, as we would expect.

.. code-block:: python

    >> from settei import get_config
    >> config = get_config('application1', 'local')
    >> print config['QUESTION']
    The Ultimate Question of Life, the Universe, and Everything
    >> print config['ANSWER']
    42

Inheriting other settings does not stop us from introducing additional ones.
Attention should be paid though as new settings could be overwritten by any
inherited ones with the same name.

.. code-block:: python

    # in your application/local_settings.py file
    def generate_config(default):

        # change a setting, the right answer is 42
        default['ANSWER'] = 42

        # introduce an additional setting
        local['NEW'] = 'A new setting'

        # this will be overwritten with the 'ANSWER' from the 'default' environment
        local['ANSWER'] = 43

        # update the 'local' settings with the 'default' settings
        local.update(default)

        # local['ANSWER'] will be 42 here again

        return local
