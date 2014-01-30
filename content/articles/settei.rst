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

:code:`settei` package is a generic purpose python settings library which uses
entry points as a registry. It is a library which provides the possibility to
define and use config settings from entry points for specific application and
environment. :code:`settei` introduces two terms, **environment** and **application**.

* **environment** is the name of an entry point
* **application** is part of group's name in which environments are defined

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
can then search for specific entry points.

Example Usage
#############

:code:`settei` package is easy on its use. The best way to explain how
:code:`settei` can be used is through examples. At first, we need to define
groups and environments. Then, we can create settings for each defined
environment and use them accordingly in the rest of the application.

Define groups and environments
==============================

As a first step, we need to define environments and put them into groups. A
group name comprises of two parts. The first of them is a standard prefix part
:code:`settings_`, and the second one is the name of an application. For
example, :code:`settings_backoffice` or :code:`settings_frontoffice`, where
:code:`backoffice` or :code:`frontoffice` is the name of the application.
The prefix part in the group name is important as it helps to identify only
entry points useful for :code:`settei` and iterate through them.

.. code-block:: python

    # in the setup.py
    setup (
        # ...
        entry_points = {
            'settings_frontoffice': [
                'default = path.to.package.of.frontoffice.default_settings:generate_config',
                'local = path.to.package.of.frontoffice.local_settings:generate_config',
            ],
            'settings_backoffice': [
                'default = path.to.package.of.backoffice.default_settings:generate_config',
                'local = path.to.package.of.backoffice.local_settings:generate_config',
            ]
        }
        # ...
    )

Each environment name inside a group must be unique. For example, in the group
:code:`settings_frontoffice` there should only be one environment named :code:`default`
and only one named :code:`local`. If we specify environments with the same name
inside a group, then a :code:`DuplicateEntryPoint` exception will be raised.
However, we can specify same environment names that belong to different groups.

Create settings
===============

Settings should be created in the :code:`generate_config` function. The :code:`generate_config`
function should return an instance of :code:`settei.config.Config` class.
Settings can be created either directly, or read them from a python file, or
from an object. If there is any error during configuration or a :code:`settei.config.Config`
is not returned, then a :code:`WrongConfigTypeError` exception is raised.

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
for the applications that we have already defined. Note that in :code:`get_config`
function we specify the application name and not the group name. For example,
if we want to load settings for the application :code:`frontoffice` and we have
defined a group of environments with the name :code:`settings_frontoffice`,
then in the :code:`get_config` function we just use the name of the application,
which in this case is :code:`frontoffice`.

.. code-block:: python

    from settei import get_config

    # get config settings for 'frontoffice' application and 'local' environment
    config = get_config('frontoffice', 'local')

    # get config settings for 'backoffice' application and 'local' environment
    config = get_config('backoffice', 'local')

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
environment that we have set.

.. code-block:: python

    # and in my_incredible_script.py we can use get_config
    from settei import get_config

    # get config settings for 'frontoffice' application and 'dev' environment,
    # which has been specified when running my_incredible_script.py
    config = get_config('frontoffice')

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
    >> config = get_config('frontoffice', 'local')
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
