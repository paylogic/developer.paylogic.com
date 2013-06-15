:title: Continuous Delivery
:date: 2013-05-30 01:08
:summary: What is Continuous Delivery and how do you get started with it?
:category: Agile
:author: Òscar Vilaplana
:slug: articles/continuous-delivery
:tags: agile, continuous delivery, deployment, release, testing, qa

*When you do Continuous Delivery you can deploy whenever you want: you
made it as easy as possible and you have become very good at it.
Everyone in the Engineering and Operations teams knows how to deploy
your application to any environment. Product can always see the latest
bells and whistles as they are built because you have Stable servers
running the latest versions of the application. You implement big
changes gradually and show them to the Product Team while keeping the
customer’s experience stable. When you decide to release, you have made
sure all things will work and you know how to react if nevertheless they
break, without fires or panic.*

*Continuous Deployment also forces you to do many right things:
repeatable builds; the exact same deployment process in all
environments, including the developer’s machines and a development
environment that is as close as possible to Production;
backwards-compatible database changes; easy rollbacks; code that is
split into components; good tests…*

Taming the Software Lion
------------------------

1800s
~~~~~

It’s the 1800s. The lion is beaten into submission through fear, brute
force and confusion. That famous tamer wielding a chair—the lion is not
scared of the chair, it’s confused of it: why is this chair floating
here? And why is this guy holding it?

Modern times
~~~~~~~~~~~~

Nowadays tamers understand the lion’s psychology. They condition the
lion to behave as they want, they tie behaviors to signals and reward
the right behaviors. They build up trust.

Taming the Software Lion—recap
------------------------------

1800s
~~~~~

It’s the 1800s. Code is beaten into submission through iterations of
half-working attempts at hand-made deployments; with fear, because it
works and we barely understand it, so don’t touch it because *it works*;
with weapons, because when it breaks it’s hacked some more until it
works (install a missing dependency, copy the forgotten templates…); and
with confusion: it’s difficult to see what’s actually installed, how,
what part of it is needed and what extra changes are needed to make it
work.

Modern times
~~~~~~~~~~~~

Nowadays software engineers understand that deploying software is hard,
and so they must get very good at it and automate it with clean
procedures so that it’s repeatable and debugable. They use continuous
integration, which rewards them with a green light when the build
passes. They take care of the health of the build. They deploy it
frequently to a staging server that the stakeholders can see. When
software breaks, they know how to act.

Engineers build up trust: they can trust that the software works and
that it does what it’s supposed to do; and the stakeholders trust them
in that the product is built to their expectations.

What You Need to implement Continuous Delivery
==============================================

To implement Continuous Delivery, you need the following:

-  A team
-  Working software
-  A repeatable build
-  An automated deployment
-  A way to rollback
-  An automated release

Team
----

Every single member of the Team must be committed to quality—process
can’t compensate for lack of commitment. This commitment includes the
constant learning of best practices and ways to improve.

Everyone in the Team must know how to deploy and release software (also
in Live) and how to maintain the deployment and release scripts.
Everyone is responsible for these scripts: there cannot be a deployment
guru. For this, the deployment scripts must be clear, concise and
simple.

All environments must be as similar as possible; this includes the
development machines. The Team must deploy the software in their
development machines using the exact same deployment and release scripts
that are used in Production and Staging.

In addition to this, everyone in the Team is responsible for:

-  Having working Stable and Production environments.
-  Having a green CI.
-  Never committing broken code.
-  Adding sufficient tests.
-  Having good quality code.

Working Software
----------------

Software, even software that *works*, is not working software unless it
has automated tests:

-  Unit Tests
-  Functional Tests
-  Acceptance Tests (testing from the user’s viewpoint, not from a lower
   layer)
-  Infrastructure and Configuration Tests (for example, testing that the
   server must be able to send e-mail).

Tests are not second-class citizens: the standards of their cleanness,
readability and maintainability must be as high as those of the rest of
the software. This quality must be maintained: tests must not be let rot
when changes accumulate.

All these tests must be run locally before committing changes and also
automatically using Continuous Integration. Because tests are executed
often they should be kept fast.

Simple mistakes, such as the ones that pylint catches, should be checked
even before running any tests.

The build must be kept green at all times. Engineers should check in
their changes often, and be ready to rollback if the change (which
passed the local tests) breaks the build. Many small changes are
preferable to a single big change: they are easier to debug and to
rollback.

Both Engineering and QA are responsible for the quality of the software
(this includes the tests).

When a test breaks, it must be fixed. There are two possible moments for
fixing it:

-  Right now. If the failure is legit, you must drop what you are doing
   and fix the it.
-  As soon as possible. If the failure is due to a false positive and
   it’s not possible to fix it right now, the test must be fixed as soon
   as possible. This should not be later than the end of the day.

If a test breaks because of changes that are being made, either the test
must be fixed right now or the changes must be reverted.

Tests cannot be disabled to be fixed later. Later won’t come any time
soon.

Any code must be peer-reviewed before being merged into the Stable
branch.

Repeatable Build
----------------

The build must be automated, and used by all members of the Team in all
environments. The build process must contain no manual steps or changes.

Deployment Script
-----------------

As for the build, the deployment script must be automated and used by
all members of the Team in all environments. Deploying the software
should be accomplished by a single command:

    *./deploy.sh* <environment> <version>

The only way to deploy is to follow the pipeline: tests, peer-review,
merge, test, automated build, automated deploy. This includes
emergencies: many problems come from skipping the pipeline and hacking a
solution out of urgency.

If the pipeline is skipped and software is deployed by hand, the system
is left on an unknown state. If the hack fails it will be very difficult
to duplicate it and investigate what went wrong. Most of the time of
fixing a problem is usually spent in searching its cause.

Rollback
--------

When a deployment fails it must be easy to rollback. There are many
strategies to accomplish this, for example Blue-Green Deployments and
Canary Deployments.

Blue-Green Deployments
~~~~~~~~~~~~~~~~~~~~~~

Have two separate environments: green is where the customers go when
they go to Production; blue is not.

#. Deploy the new version on blue.
#. Test blue and do manual acceptance.
#. Switch blue to green and green to blue: now Blue is serving
   Production

If the deployment goes wrong, rolling back is a matter of switching
green and blue. It’s easy to investigate what went wrong because blue is
still running the new code.

Canary Deployment
~~~~~~~~~~~~~~~~~

Deploy the new version on a fraction of the servers and have it run
alongside the old version. Once it’s confirmed that it works as
expected, extend the deployment to the rest of the servers.

This strategy can also be used to do A/B testing or assessing the
performance impact of new features.

Rollback the Database
---------------------

For rollbacks to be possible, the database changes must be kept
backwards compatible. There is no way around this. When this is not
possible, make a plan on how to rollback.

Automated Release
-----------------

When all the previous steps are in place, an automated release is just
the last step on the chain. While an automated release to Production may
not be desirable in all cases, an automated release to a Staging or
Integration environment will allow the stakeholders to use the latest
version of the software while it’s being developed and before it goes to
Production.

Frequent, smaller changes are preferred to a big release: small releases
have shorter Time to Recover: if it goes wrong it will be easier to find
what went wrong if the amount of changes is small.

Releasing is hard. If it hurts, do it more often.

Hidden Features
~~~~~~~~~~~~~~~

In some cases it is useful to release features but keep them
inaccessible or only accessible to a few users. There are several tools
to make this easy;
`gargoyle <https://github.com/disqus/gargoyle>`_
is a popular one for Django.

Tips
----

Split In Components
~~~~~~~~~~~~~~~~~~~

Split your software in components that can be deployed independently.

A component:

-  Is reusable
-  Is replaceable with something else that implements the same API.
-  Is independently deployable.
-  Encapsulates a coherent set of behaviors and responsibilities of the
   system.

Splitting your software in components encourages a clear delineation of
responsibilities and makes understanding and changing the code easier.

Rehearse Releases
~~~~~~~~~~~~~~~~~

Releasing is hard. Rehearse it and get very good at it.

Manage your Infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~

Write tests that verify that your infrastructure behaves as you expect
and provides the necessary functionality.

Automate all infrastructure changes that can be automated, and document
the rest.

Equal Environments
~~~~~~~~~~~~~~~~~~

All environments must be as similar as possible. Use
`vagrant <http://www.vagrantup.com/>`_
to develop.

Automate Everything
~~~~~~~~~~~~~~~~~~~

A process that is automated is repeatable and easier to debug. Automate
everything that can be automated.

--------------

I gave a talk about this at DjangoCon Europe 2013. Here are the
`slides <https://bitbucket.org/grimborg/continuousdeployment/src/tip/continuous-deployment.pdf>`_;
the video will be available soon.

If this interests you, you may want to check these books:

-  `Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation <http://www.amazon.com/Continuous-Delivery-Deployment-Automation-Addison-Wesley/dp/0321601912/ref=sr_1_1?ie=UTF8&qid=1369904950&sr=8-1>`_
-  `Continuous Integration: Improving Software Quality and Reducing Risk <http://www.amazon.com/Continuous-Integration-Improving-Software-Reducing/dp/0321336380/ref=sr_1_1?ie=UTF8&qid=1369905064&sr=8-1>`_
-  `Agile Testing: A Practical Guide for Testers and Agile Team <http://www.amazon.com/Agile-Testing-Practical-Guide-Testers/dp/0321534468/ref=sr_1_1?ie=UTF8&qid=1369905098&sr=8-1>`_
-  `Test Driven Development: By Example <http://www.amazon.com/Test-Driven-Development-Kent-Beck/dp/0321146530/ref=sr_1_1?s=books&ie=UTF8&qid=1369905116&sr=1-1>`_
