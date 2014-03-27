:title: Settei
:date: 2014-01-29 12:03
:summary: Settings configuration system based on entry points of setuptools
:category: Open source
:author: Spyros Ioakeimidis
:slug: articles/settei
:tags: open source, python, settings, entry points, setuptools

:code:`settei` is a generic purpose python settings library based on the concept of
entry points as a registry, inspired by
`setuptools <http://pythonhosted.org/setuptools/pkg_resources.html#entry-points>`_.

.. contents::

Introduction
############

:code:`settei` is a generic purpose python settings library which uses entry
points as a registry. It is a library which provides the possibility to define
and use configuration settings from entry points for specific applications and
environments. :code:`settei` introduces the following terms:

* **environment** is the name of an entry point
* **group** is a group of defined environments
* **application** is part of a group's name and refers to the application to which
  settings apply

A minimal app that illustrates the use of `settei` can be found
`here <https://github.com/paylogic/settei-example>`_.

Motivation
##########

In Paylogic, we are extensively using `Django <https://www.djangoproject.com/>`_
web framework for most parts of our system. Django uses the concept of
`setting files <https://docs.djangoproject.com/en/1.6/topics/settings/>`_, in
which we can define application-specific settings, such as ``DEBUG``. In the
rest of the application we can access these settings using for example
:code:`django.conf.settings.DEBUG`. However, for other parts of our system we
are using `Flask <http://flask.pocoo.org/>`_, which follows a similar, but not exactly
the same way to define `configuration settings <http://flask.pocoo.org/docs/config/>`_.
In a Flask application a setting could be accessed like :code:`app.config['DEBUG']`.

Soon we were confronted with the limitation to share configuration settings
between Flask and Django applications. Additionally, we wanted to keep these
configurations consistent. However, we found out that there was no framework-agnostic
python library for specifying configuration settings.

Moreover, as we have a clear separation between environments (e.g. dev, staging,
live etc.), some configuration settings are either set in one environment and not
in the others, or the same configuration settings have different values depending
on the environment. The code however, should not know anything about the environment
in which it is executed. In this way the code does not need to be modified, even
when multiple environments are used.

For this reason, we initially decided to create separate files to store configuration
settings, which could also change depending on the environment. However, we end
up with many of these files, which at some point became cumbersome to maintain.
Furthermore, other developers started importing settings from these files and
others used the standard way of Django. The result of this is inconsistencies
and conflicts, as the same setting can be imported from different places.

Requirements
============

Based on this motivation, we came up with a number of requirements for a settings
configuration system.

* Introducing a new environment should be easy and without too much hassle.
* We should have the possibility to inherit/extend settings from other environments.
  This would allow to build a modular and extensible structure of configuration
  settings.
* There should be no involvement of specific template structure for generating
  settings, because it is getting really hard and cumbersome to read templates
  with tons of expressions.
* It should be possible to store settings separately from applications and
  scripts. The advantage of this is that we can create secret settings in a way
  that makes them also safe and that do not depend on a specific application.
* A configuration settings system should be framework-agnostic so it can be used
  when multiple frameworks are involved.

Design
######

The most important design decision of :code:`settei` is to base its implementation
in the concept of entry points, in order to create a framework-agnostic library
for configuration settings.

Entry points
============

Entry points provide an intuitive way for distributions to expose Python objects,
such as functions or classes, to be used by other distributions. Applications
can then search for specific entry points. :code:`settei` uses the concept of
entry points to define groups of environments.

So, what does using entry points mean? It means that we will have the possibility
to store settings in a distribution. Then, if we want to get access to settings of
e.g. a default or a local environment, we will need to have access install to this
distribution and include this distribution in ``PYTHONPATH`` of the script or application.

Groups and environments
-----------------------

A group is a container of environments. An example of a group with two environments
could be:

.. code-block:: python

    'settings_application_name': [
        'default = path.to.package.of.application_name.default_settings:generate_config',
        'local = path.to.package.of.application_name.local_settings:generate_config',
    ]

The name of the group consists of two parts.
The first of them is a standard prefix part :code:`settings_`, and the second
one is the name of an application. For example, :code:`settings_application_name`,
where :code:`application_name` is the name of the application. The prefix part in
the group name is compulsory as it helps :code:`settei` to identify only entry
points useful for it and iterate through them.

Each environment name inside a group must be unique. In our example, in the
group :code:`settings_application_name` there should only be one environment named
:code:`default` and only one named :code:`local`. If we specify environments
with the same name inside a group, then a :code:`DuplicateEntryPoint` exception
will be raised. This exception is used to avoid cases of scripts ``borrowing``
settings from each other. However, we can specify same environment names that
belong to different groups.

Example Usage
#############

:code:`settei` package can be configured and used in a series of simple steps.

1. Define groups and environments in ``setup.py`` of package.
2. For each environment (e.g. default_settings), define the function to be used
   as an entry point.
3. Implement this function in the environment files (e.g. default_settings.py),
   which should create and return a new instance of :code:`Config`
   with configuration settings for this environment.
4. Use the :code:`get_config` function in the rest of the package to read
   configuration settings for specific applications and environments.

The best way to explain how :code:`settei` can be used is through examples.
The rest of this section goes into more detail for each of the aforementioned steps.

Define groups and environments
==============================

As a first step, we need to define environments and put them into groups. We are
free to choose the name of the function to be used as an entry point. In this case,
we chose the name :code:`generate_config`. Let's assume that our package contains
two applications.

.. code-block:: python

    # package/setup.py
    setup (
        # ...
        entry_points = {
            'settings_application1': [
                'default = path.to.application1.default_settings:generate_config',
                'local = path.to.application1.local_settings:generate_config',
            ],
            'settings_application2': [
                'default = path.to.application2.default_settings:generate_config',
                'local = path.to.application2.local_settings:generate_config',
            ]
        }
        # ...
    )

Create settings
===============

To create settings, we need an instance of the :code:`Config` class.
In the following example, we are using the function named :code:`generate_config`,
which we specified as an entry point when we defined the groups and environments.
The :code:`generate_config` function, in our case, returns an instance of the
:code:`Config` class. Settings can be created either directly,
read them from a python file, or from an object. If there is any error during
configuration or a :code:`Config` instance is not returned, then
a :code:`WrongConfigTypeError` exception is raised.

.. code-block:: python

    # package/application1/default_settings.py
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

In order to use the settings of our package, we need to first install it using
:code:`python setup.py install` and make sure that it is in out path. We can then
read and use settings in the rest of our package
by using the :code:`get_config` function. Note that in :code:`get_config`
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

If the environment from which we want to read settings does not exist, then an
:code:`EnvironmentNotSpecified` exception is raised. Another way to define the
desired environment is using the :code:`CONFIG_ENVIRONMENT` variable.

.. code-block:: python

    # run in this way
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
you want your :code:`local` settings to inherit the :code:`default` settings,
then in the :code:`generate_config` function you should mention the name of
environment from which you want to inherit.

.. code-block:: python

    # in your application1/local_settings.py file
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

    # in your package/application1/local_settings.py file
    from settei.config import Config

    def generate_config(default):
        local = Config()

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

If the provided environment in :code:`generate_config` is missing or not
specified, then an :code:`EnvironmentIsMissing` or :code:`EnvironmentNotSpecified`
exception will be raised respectively. If we try to specify more than one
environments to inherit settings from, then a :code:`MoreThanOneDependencyInjection`
exception will be raised.

Conclusion
##########

:code:`settei` is a package, which bases its implementation on the concept of
entry points from setuptools, to provide a maintainable way of creating configuration
settings. :code:`settei` makes it very easy and intuitive to introduce a new environment,
e.g. a live environment, where settings usually differ a lot from those used
during development. Finally, settings inheritance, which is accomplished by using
dependency injection, provides this modularity and extensibility we were in need of.
