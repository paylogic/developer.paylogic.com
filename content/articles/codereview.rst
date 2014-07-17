:title: Paylogic Code review tool
:date: 2014-07-17 9:00
:summary: Paylogic made its code review tool open source, in this article we'll talk about its internals in detail.
:category: Open source
:author: Anatoly Bubenkov
:slug: articles/codereview
:tags: code review, gatekeeper, fogbugz, review, rietveld, open source


Introduction
============

As open sourcing software is a strategic decision of Paylogic we decided not to make an exception for our 
development tools, in the hope that they are of use to the community. The code review tool is probably our most 
important development tool, so we decided to start with that. The Github repository can be found 
`here <https://github.com/paylogic/codereview>`_.

`Code review <http://en.wikipedia.org/wiki/Code_review>`_ is one of the main pillars of the Paylogic development
process. We have multiple projects ongoing, and none of the code changes can go into the stable repository
without at least 2 code reviews. The last code review is done by a special company role - ``Gatekeeper``.

We will reveal more about the gatekeeper process in later articles, but you can already see that code reviewing
is a very important process for us, so the tool we use for it is important as well.

This article covers and explains the choice of the tool, its customizations, and the use case.


The Choice
==========

In 2011 we had to choose a code review tool, and after a thorough research
`rietveld <https://code.google.com/p/rietveld/>`_ seemed one of the best solutions for our specific needs:

* Web based.
* Minimalistic, code centric interface.
* Has keyboard shortcuts for easy code review navigation.
* Written in python, so it's easy to change and maintain.
* Has a community which improves it constantly.
* Simple installation on a private server.


Customizations
==============

So we decided to use rietveld. But we had to customize it significantly as our development process uses
`Fogbugz <https://www.fogcreek.com/fogbugz/>`_ as a case management tool. This means that every change to the 
Paylogic codebase has a reference to a Fogbugz case, and the development itself is case-based.

The whole picture of our continuous integration will be described in later article(s), however there was a
`great talk <http://www.slideshare.net/zittersteyn/advanced-continuous-integration-pygrunn-2014-dirk-zittersteyn>`_
at our `PyGrunn <http://pygrunn.org/>`_ conference
on this topic from `Dirk Zittersteyn <http://nl.linkedin.com/in/dzittersteyn>`_.  However, since it is important
to understand the role the code review tool plays in our ecosystem, the below image shows a part of the process.

.. image:: |filename|/images/codereview/gatekeepering-and-code-review-process.png
    :align: center
    :alt: gatekeepering and code review process

As you can see from the diagram (and the Legend), the code review tool is a critical part of our process.

Before we continue, we'll give you a quick glossary for the rest of this article:

``original repository`` (``target repository``)
    Version control repository which is considered as a target in which to merge some proposed set of changes.

``original branch`` (``target branch``)
    Version control branch in the ``original repository`` in which to merge some proposed set of changes.

``feature repository`` (``source repository``)
    Version control repository which is considered as a source of the proposed set of changes. This can be the same as
    ``original repository``.

``feature branch`` (``source branch``)
    Version control branch in the ``source repository`` which is considered as a source of the proposed
    set of changes.

With the customizations we've made to ``rietveld``, we can now:

Use corporate single sign-on to authorize users in the code review tool
----------------------------------------------------------------------

It's important to remove unnecessary additional user management responsibilities from our Operational IT team. And of
course, from the user's perspective it's much less effort, as they can use a single corporate account to log in
(we use `Google Apps for Business <http://www.google.com/enterprise/apps/business/>`_)

Create code review issues (patchsets), taking any required information from the corresponding Fogbugz case
---------------------------------------------------------------------------------------------------------

This feature is implemented by creating a special endpoint on the code review tool which gets the case number as
a parameter, and retrieves the following fields from that case through the
`Fogbugz API <http://help.fogcreek.com/8202/xml-api>`_:

* Original (target) branch (for example ``master`` or ``default``) - implemented using a custom field in Fogbugz.
* Feature (source) branch (for example ``nice-feature``) - implemented using a custom field in Fogbugz.

For custom fields, we use the `Custom Fields <http://www.fogcreek.com/fogbugz/plugins/plugin.aspx?ixPlugin=1>`_ plugin.
From the Fogbugz side, it looks like this:

.. image:: |filename|/images/codereview/create-patchset.png
    :align: center
    :alt: create patchset from Fogbugz

Apply custom validations for any patchsets created
--------------------------------------------------

We implement some critical checks, where we for example don't allow the changing of certain non-editable files.
If any of the validations didn't pass, creation of the issue (i.e. an additional patchset) fails and shows an error
to the user.

Implement Gatekeepering process support
---------------------------------------

Users with a special role can now ``approve`` a certain revision of the feature branch.

This is, again, implemented using a special custom field in Fogbugz called
``approved revision``, together with the Fogbugz API to set it from the code review tool.

In the code review tool:

.. image:: |filename|/images/codereview/approve-revision-click.png
    :align: center
    :alt: approve revision from codereview by the gatekeeper, target branch autocompletion

And in Fogbugz:

.. image:: |filename|/images/codereview/approved-revision-field.png
    :align: center
    :alt: approved revision and ci project fields set in the Fogbugz

Allow ``gatekeepers`` to set (and select from the dropdown) the ``target branch`` for a given ``CI project``
------------------------------------------------------------------------------------------------------------

Both ``target branch`` and ``CI project`` are custom fields of a Fogbugz case.

In the code review tool:

.. image:: |filename|/images/codereview/approve-revision-target-branch.png
    :align: center
    :alt: approve revision from codereview by the gatekeeper, target branch autocompletion

And in Fogbugz:

.. image:: |filename|/images/codereview/target-branch-field.png
    :align: center
    :alt: target branch field in the Fogbugz

Support creation of an issue (patchset), using ``bzr``, ``git`` and ``mercurial`` repositories
----------------------------------------------------------------------------------------------

All combinations are accepted for ``original`` and ``feature`` branch fields in Fogbugz.
As additional protection from ``phishing`` on the ``original`` branch, the latest revision from
the ``source repository``'s ``original branch`` will be used to calculate a diff between
the ``source repository``'s ``feature branch`` and the ``original repository``'s ``original branch``.


Problems using rietveld
=======================

rietveld was developed specially for `Google App Engine <https://developers.google.com/appengine/?csw=1>`_.
It has lots of benefits for developers who don't want to bother with any OpIT related tasks.
As we however have a strict requirement to host the code (and thus the code review tool) on our private servers, we used
`gae2django <http://django-gae2django.googlecode.com/svn/trunk/examples/rietveld/README>`_ to deploy rietveld locally.
What gae2django does is convert models that are supposed to be used with the
Google App Engine datastore to Django ORM models. This allows us to deploy the
application using relational databases such as (in our case) MySQL.

This was ``good enough`` for us, as up till now rietveld was using GAE DB (ext.db). But this is no longer the case.
Now rietveld uses `NDB <https://developers.google.com/appengine/docs/python/ndb/>`_ for its models. And it's simply
``not possible`` to implement automatic mapping from NDB-based models to django ORM models
because the difference is huge.

So currently, we are in the situation that we cannot receive any updates from the rietveld repository any more,
so instead we have to support our ``fork`` ourselves. For now this is ``acceptable``,
but we are considering moving to a different code review tool.


Want to use it or to try it?
============================

The `readme <https://github.com/paylogic/codereview/blob/master/README.rst>`_ on Github contains all the information
required to set up the code review tool on your server. Don't hesitate to try it out.
If you have any problems with installation, please create an `issue <https://github.com/paylogic/codereview/issues/>`_
on Github.


Future considerations
=====================

As was mentioned earlier, ``Review Board`` will probably be the replacement for
our current solution. However, if we'll switch to git completely (which we haven't done yet) there are
some other alternatives to consider as well, such as:

* `GitLab <https://www.gitlab.com/>`_
* `Gerrit <https://code.google.com/p/gerrit/>`_

Any new tool we might choose will have to be customized in order to be an integral part of our development process.
This new customization will be open sourced as well.


"Thanks! Questions?"
====================

So regarding the code review, we've put all our cards on the table: from decision making to implementation,
support, and use cases. We hope that it will be useful for the community.
Feedback is, as usual, more than appreciated. Happy code reviewing, we wish you 0 comments on your reviews!
