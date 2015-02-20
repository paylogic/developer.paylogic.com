:title: Lessons learned using SCRUM
:summary: At Paylogic we've come a long way, from ad hoc development to a
          formalized SCRUM approach. We want to describe our lessons from this
          journey.
:category: Agile
:author: Lars de Ridder
:date: 2014-10-09 10:28
:slug: articles/lessons-scrum
:tags: scrum, agile, project management, scrum master, product owner
:email: lars.de.ridder@gmail.com

.. contents:: Table of Contents
   :depth: 2

Introduction
============

Paylogic has been using `SCRUM`_ for its engineering process for years now.
We've made quite a bunch of changes throughout this time and learned a lot.
Right now we have a highly repeatable and predictable development process, which
makes it very easy for new engineers to start and almost guarantees that a
commitment will be met. I would like to share some of the most important things
we've learned along the way.

When doing SCRUM, do SCRUM
==========================

There are way too many companies out there doing something and calling it SCRUM
(or agile), and not actually doing it. You have the opportunity to stand on the
shoulders of giants. Use those giants, especially when just getting started.
Understand why things are done, and only then modify if needed. Avoid ScrumButs_
as much as possible.

And if it turns out you don't like SCRUM, use something else, but don't play
pretend.

There really isn't much process
===============================

There's some, more than with ad hoc programming, and a bit more than with
Kanban_, but definitely not a lot.

At Paylogic, in an average two week sprint with three teams of in total 14
engineers, we spend two hours on sprint planning, half an hour per team on
backlog grooming, about 20 minutes on the sprint demo and about 40 minutes on
the sprint retrospective. Then we of course have standups, which take about 10
minutes per day and are done on all days except for the sprint planning day.

This totals to five hours of process per person per two weeks, or two and a half
hours per week. Based on a 40 hour work week, that's about 6%.

The process that exists is good!
================================

Now 6% is all well and good, but every bit of process is too much if it has no
outcome. However, the structure of SCRUM merely asks you to do what you should
be doing already. Basically, you should:

#. Work in iterations;
#. Make a plan for each iteration so that the business knows what's coming;
#. Keep each other updated on your progress and your issues;
#. Show off what you created; and
#. Evaluate your iteration and take action to improve.

I find it hard to find fault in any of those steps, and they are basically the
only steps you have to do to implement SCRUM.

Timebox your meetings
=====================

Meetings have a tendency to drag on (see also `Parkinson's Law`_). It's fairly
simple to prevent this however.

In all SCRUM meetings (and most productive meetings actually), you are dealing
with a number of consecutive items, and when all are handled you're done. In the
case of the sprint planning each item is every story that fits in the sprint,
and in the case of a standup it's each member of the team. Simply set a deadline
for each item and track and enforce this deadline. People will focus on the most
important points to most optimally use their time, and after a few times, almost
no-one will get even near to the deadline.

Team members should be in charge of their individual velocity
=============================================================

Engineers take pride in doing their work well. Creation is in our blood. It
should be natural to leave it up to the engineer to determine the speed in which
they feel they work, or want to work. Velocity should not automatically be
computed by a script or mandated by a team leader, and should not be averaged
out over a team. It is important to recognize the individuals in a team, and
they should have the opportunity to set their own velocity based on past results
and future ambitions.

Next to that, it also makes planning a lot easier. If you have 80 story points
available in a sprint, it usually doesn't mean that you can plan a single story
estimated on 80 story points in that sprint. Work is often not that
parallelizable. If two persons can work on this story, and each person has 20
story points as their own velocity, then it's suddenly simple to see that you
can do 40 story points of that story.

Use proper tooling
==================

I wrote an article on `how we use Trello`_, but any tool or method that allows
you to visualize the work being done and shows your progress towards the end of
the sprint is fine. Don't skip this; not having it basically means flying blind,
and you won't ever get controlled sprints.

Plan everything
===============

Don't only plan for the user stories scheduled for a sprint. Recognize that
other work also has to be done. In our case, we had a period where we had to
reduce the commitment every sprint, because one of the engineers had to perform
maintenance on the new Continuous Integration server regularly. Keep monitoring
which work is actually done, and make sure to create space for this work to be
planned as well.

Backlog grooming is essential
=============================

We started `backlog grooming`_ relatively late, as we didn't think we needed it.
Turns out we did. It's really nobody's fault but the team's if it finds out
during sprint planning that a user story isn't ready for the sprint. And then
there's no time to correct it, with frustrations on all sides.

Don't try to actually do estimations or even think of tasks during the grooming
sessions. The team should simply review each user story to see if they can work
on it in its current state.

A team also needs freedom when determining what to do
=====================================================

The product owner is of course responsible for the backlog, but to get good
software, the team needs to be able to influence what they work on as well.  The
team needs some room to, for example, improve its tooling and development
environment and to iterate over earlier designs. It is essential for a product
owner to take this into account.

If this turns out to be difficult to negotiate, balance can be restored by
allowing the team to schedule a portion of its time (say 10%) by itself,
regardless of the backlog.

Commitment vs forecast
======================

In the official SCRUM description, there actually exists no such thing as a
commitment. Instead, there is a forecast_. The idea of this forecast instead
of commitment is great, the thing is however that often it doesn't matter.
Whether you use the term forecast or commitment, business people will still
expect you to deliver what you said you would deliver. Because that's how they
work.

There's no real cure for this. Communication is very important here, but in the
end it's just something you should be aware of. Don't expect you can just win
this by changing the term. You'll have to change a mindset, and sometimes even a
culture, and that's much harder.

Multiple teams can SCRUM together
=================================

Having a separate SCRUM team doesn't mean they have to have their own standups
and retrospectives. In fact, that's often a bad idea. If the teams are
completely independent, kind of like different companies, then it's of course
fine. But usually, when you are part of the same company, you work together on
different parts of the same whole, and communication between teams is just as
important as communication within teams.

In our case, the three teams consist of a total of about 14 members. This is
small enough so that we can still have communal standups and retrospectives.
Sprint planning and backlog grooming are done separately however.

When teams get larger, a `SCRUM of SCRUMS`_ can be used to keep communication
going.

Closing thoughts
================

At Paylogic we've seen our process grow from being used in a single, small team,
to a single large team, to scaling to three teams. We've seen people come and
go, but the process is still going strong. I am very happy with it and with the
performance of the teams as well.

Regardless, there are other alternatives that can work just as well, or perhaps
even better. When it comes to raw productivity, I actually think a Kanban
process is just a little bit better. A sprint ending and beginning is still
disruptive and does reduce productivity, more than just the hours spent on the
meetings. Kanban, being a continuous process, doesn't have this.

It does require more discipline to pull off correctly however, and I believe it
is harder for a newcomer to get started with. I would like to try such a process
in Paylogic however, so perhaps I'll write another article about that by that
time.

.. External references:
.. _SCRUM: https://www.scrum.org/
.. _ScrumButs: https://www.scrum.org/scrumbut
.. _Kanban: http://en.wikipedia.org/wiki/Kanban_%28development%29
.. _Parkinson's Law: http://en.wikipedia.org/wiki/Parkinson%27s_law
.. _how we use Trello: trello.html
.. _backlog grooming: http://scrummethodology.com/scrum-backlog-grooming/
.. _forecast: https://www.scrum.org/About/All-Articles/articleType/ArticleView/articleId/95/Commitment-vs-Forecast-A-subtle-but-important-change-to-Scrum
.. _SCRUM of SCRUMS: http://guide.agilealliance.org/guide/scrumofscrums.html
