:title: pip-accel: Accelerator for pip, the Python package manager
:summary: Recently we published `pip-accel` to GitHub_ and PyPi_ and in this article we'll tell you why and how we created this project.
:category: DevOps
:author: Peter Odding
:date: 2013-05-14 00:28
:slug: articles/pip-accel
:tags: python, deployment, virtual environments, automation, pip, open source, packaging

Recently we published `pip-accel` to GitHub_ and PyPi_ and in this article
we'll tell you why and how we created this project.

.. contents::

Let's dive in:

At Paylogic we deploy our code bases a lot
##########################################

Currently we have the following environments where we deploy our code bases:

- Work laptops of the engineers and devops
- Continuous integration server with 10 slaves (we are using Jenkins_)
- Stable testing environment (continuously deployed)
- Staging testing environment (managed w/ releases)
- Production servers

In some of these environments (specifically in the continuous integration and
stable environments) new code bases can be deployed every few minutes when
engineers are publishing new changes or tested changes are being merged into
the main repository.

Python deployment strategies
============================

For Python deployments there are two main ways to deploy a project and its dependencies:

1. System-wide installation
2. `Virtual environments`_ (or an equivalent construction, isolated from the system)

At Paylogic we use system-wide installations on production (like) hosts and
virtual environments everywhere else. Why don't we use virtual environments on
production systems? Virtual environments do have some drawbacks (see below) and
we have the luxury of being able to isolate applications on the level of
virtual machines instead of Python virtual environments. This additional layer
of isolation is worth it for us.

Drawbacks of virtual environments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python virtual environments are by their nature a bit fragile. Quoting from
`the virtualenv website`_:

    **Warning:** *Python bugfix releases 2.6.8, 2.7.3, 3.1.5 and 3.2.3 include
    a change that will cause import random to fail with “cannot import name
    urandom” on any virtualenv created on a Unix host with an earlier release
    of Python 2.6/2.7/3.1/3.2, if the underlying system Python is upgraded.
    This is due to the fact that a virtualenv uses the system Python’s standard
    library but contains its own copy of the Python interpreter, so an upgrade
    to the system Python results in a mismatch between the version of the
    Python interpreter and the version of the standard library. It can be fixed
    by removing $ENV/bin/python and re-running virtualenv on the same
    target directory with the upgraded Python.*

Big projects have a lot of dependencies
=======================================

At Paylogic we create large virtual environments with pip_: At the time of
writing our main code base has 84 dependencies if we include testing,
documentation and transitive dependencies (43 of those dependencies are required
in production). Some of these dependencies require SWIG and a compiler and for
large modules the compilation can take a while.

pip can be slow and unreliable
==============================

So we build a lot of virtual environments which can be really slow. The actual
creation of the environment only takes a couple of seconds, but installing all
of the dependencies can take minutes! For example at the time of writing it
takes about seven minutes to install all dependencies of Paylogic's main code
base using pip_.

What's worse is that PyPi and distribution websites can be very unreliable.
One day everything works fine, the next day the same packages you downloaded
previously can no longer be downloaded. Usually these are transient errors, you
just have to be very patient and/or retry until it works.

We love virtual environments and pip so we don't necessarily need to replace
either of those, but it would be nice to solve these two problems.

Optimizing pip
##############

In this section we'll discuss ways in which we can speed up pip.

Brute force caching
===================

If no requirements changed, we can re-use a previously built and cached virtual
environment. Terrarium_ takes this approach. There is a drawback however: If a
single dependency changes, we can't re-use the cache and have to rebuild
everything. This is not exactly ideal for continuous integration/deployment
environments (which is a big use case for us).

So what about a more granular approach?
=======================================

There are two obvious targets:

1. Given absolute version numbers available in the download cache, pip_ still
   goes out and scans PyPi and distribution websites. This is documented
   behavior:

      pip offers a ``--download-cache`` option for installs to prevent redundant
      downloads of archives from PyPI. The point of this cache is not to
      circumvent the index crawling process, but to just prevent redundant
      downloads. Items are stored in this cache based on the url the archive
      was found at, not simply the archive name. If you want a fast/local
      install solution that circumvents crawling PyPI, see the `Fast & Local
      Installs`_ Cookbook entry.

2. Binary packages are recompiled for every virtual environment. This is
   because historically pip_ did not support binary distributions (support for
   the Wheel_ format is now coming) so the only option was to go for source
   packages, which require compilation. However there is of course no reason
   why previous results can not be reused.

Keeping pip off the internet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Our first problem was that pip's index crawling process is very slow so we want
to avoid it when possible. So how can we keep pip_ from always scanning PyPi
and distribution websites, even when all of the dependencies are already
available in the local download cache? Here's how:

1. We generate a local source package index based on the pip_ download cache.
   This local source package index is just a directory with source packages
   downloaded from PyPi and distribution websites.

2. We then run pip_ as follows:

   .. code-block:: sh

      $ pip install --no-index --find-links=file://$LOCAL_INDEX --requirement=example.txt

   If the command succeeds it means all of the requirements (including the
   transitive dependencies) can be satisfied from the local index. In this case
   we don't need a network connection!

Caching compiled packages
~~~~~~~~~~~~~~~~~~~~~~~~~

Our second problem was that pip_ always recompiles binary modules. This isn't
very hard to fix. Here's how you create a dumb binary distribution (a tar
archive with binary artifacts specific to your current system):

.. code-block:: sh

   $ python setup.py bdist_dumb --format=gztar

Unfortunately these distributions are really dumb:

.. code-block:: sh

   $ tar tf ipython-0.13.2.linux-x86_64.tar.gz | tail -n1 | echo 'foo'
   ./home/peter/.virtualenvs/pip-accel/lib/python2.6/site-packages/IPython/lib/security.py

Dumb binary distributions contain hard coded pathnames specific to the virtual
environment we created them for! This is useless in any other context. Of
course with a bit of work these pathnames can be normalized to the root of the
(virtual) environment...

Putting it all together: pip-accel
##################################

So now you know why and how pip-accel_ was born! It's available on PyPi_ and
GitHub_ but if you just want to try it out you can use the following:

.. code-block:: sh

   $ pip install pip-accel

The command ``pip-accel`` will be installed in your environment. You should be
able to use it just like pip_, simply type ``pip-accel`` where you would
previously type ``pip`` on the command line (you can even alias it if you
like).

How fast is it?
===============

To give you an idea of how effective ``pip-accel`` is, below are the results of
a test to build a virtual environment for our main code base:

=========  ================================  ===========  ===============
Program    Description                       Duration     Percentage
=========  ================================  ===========  ===============
pip        Default configuration             444 seconds  100% (baseline)
pip        With download cache (first run)   416 seconds  94%
pip        With download cache (second run)  318 seconds  72%
pip-accel  First run                         397 seconds  89%
pip-accel  Second run                        30 seconds   7%
=========  ================================  ===========  ===============

We have some ideas on how to make this even faster :-)

More information
================

If you're interested in more details, the readme on GitHub contains more
information about the `internal control flow`_. You're also free to browse the
`source code`_; it's only a few hundred lines of well documented Python code.

.. External references:
.. _Fast & Local Installs: http://www.pip-installer.org/en/latest/cookbook.html#fast-local-installs
.. _GitHub: https://github.com/paylogic/pip-accel
.. _internal control flow: https://github.com/paylogic/pip-accel#control-flow-of-pip-accel
.. _Jenkins: http://jenkins-ci.org/
.. _pip-accel: https://github.com/paylogic/pip-accel
.. _pip: http://www.pip-installer.org/
.. _PyPi: https://pypi.python.org/pypi/pip-accel
.. _source code: https://github.com/paylogic/pip-accel/blob/master/pip_accel.py
.. _Terrarium: https://pypi.python.org/pypi/terrarium
.. _the virtualenv website: http://virtualenv.org/en/latest/news.html
.. _Virtual environments: http://www.virtualenv.org/en/latest/
.. _Wheel: http://wheel.readthedocs.org/en/latest/
