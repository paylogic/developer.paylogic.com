:title: How we use Trello and some custom tooling to streamline our development process
:summary: We oriented our development process around Trello. We will describe
          how we use it and augmented it using a few custom solutions.
:category: Agile
:author: Lars de Ridder
:date: 2014-10-07 12:05
:slug: articles/trello
:tags: trello, fogbugz, burndown, scrum, agile
:email: lars.de.ridder@gmail.com

.. contents:: Table of Contents
   :depth: 2

Introduction
============

One of the challenges in the abstract world of code (and at the same time one of
the most rewarding things you can do) is to visualize the work that is being
done and that is left to do. Code is not like buildings that you can see rising
from the ground, and not even like a book that you can count the pages. This
makes it incredibly hard to gauge progress and view the status.

Luckily we live in a magical world where not only there is such a thing like
code and computers to interpret it, but there are also people building awesome
things with them to solve problems. One of these things is of course Paylogic,
but another (and the thing that we will actually talk about here) is `Trello`_.

In this article you will see how we at Paylogic use Trello, combined with custom
tooling through the power of API's, to make our development process just a bit
better.

In the beginning
================

The earth was flat, and Paylogic only used `FogBugz`_. If you're not familiar
with FogBugz, it's a bug tracking tool created by `Fog Creek`_ that is fairly
easily extensible with `plugins`_, which is what we did. Everyone got assigned a
case at the start of the week (I want to say sprint, but it wasn't a sprint),
and you worked on your case until it was finished, and you would get another
case. Cases came from a single prioritized list, and were assigned by the team
leader based on FTE's and estimations of hours of work.

So what exactly was wrong with this approach? Many things (many, many things),
but what I want to focus on now is that there was no way for anyone to get an
insight on how things are going and what the progress is. Sure, you could go to
an individual case and see how many hours were registered on it. If you believe
in a fairy tale world where an hour registered directly correlates with an hour
less work to be done it would be fine, but that's not the case. As you can
imagine, this led to many issues towards the end of a week, were tasks weren't
finished and no-one knew what was going on.

Evolution
=========

This approach evolved quite a bit before arriving to our current point. One of
the things was the introduction of a `Kanban plugin`_ in FogBugz, which allowed
people to see in which sprint which case would be done. An obvious improvement,
but not yet enough.

Another was to simply use stickies on a wall. While this was nice and tangible,
it also had its downsides. A burndown had to be drawn by hand (what are we,
peasants?), and there was a bit of a barrier (however tiny) to get up, walk over
to the board and create a card if you need one. This caused many fires to be
undocumented, as it was actually easier to just fix the fire instead of
following the process.

And of course, there was no log of past sprints, a huge downside as well. And it
didn't scale. And stickies started falling of the wall. You get my point.

Enter Trello
============

To quote from their site: "Trello makes it easy to organize anything with
anyone". Lucky for us, it does indeed. We now use it as the main board for
our teams to register their work and the progress, as well as keep track of the
backlogs.

Sprint board
------------

A typical sprint board of one of our teams looks something like this:

.. image:: |filename|/images/trello/sprint-board.png
    :align: center
    :alt: Sprint board

Let's go through the columns (or lists in Trello's terminology).

- *User stories*: The user stories committed for this sprint. Each of these has
  a case number, written in front of it, and an estimate, written behind it
  between brackets. Our "knots" are basically story points.
- *User stories - Done in sprint*: The user stories that fulfill the Definition
  of Done, at least for within the sprint. In our case, user stories often
  aren't deployed during a sprint, so there's a separate Definition of Done for
  that.
- *To Do*: This column contains the **tasks** of the user stories that still
  have to be done. The tasks are not really linked to user stories (Trello does
  not provide such functionality between cards), but by using the same case number and the
  same color, we can visually distinguish them quite easily.
- *Doing*: This are tasks that are currently in progress.
- *Done*: All tasks that are completed will end up here.
- *Fires*: All fires encountered. We often use a placeholder to keep a buffer
  for unexpected work.
- *Fires Done*: A fire that was worthy to be done will end up here.

After the sprint planning, a new sprint board is created for each team, where
they create cards for the user stories and the tasks. The commitment is
generated from the user stories of each team, and as such identical to what is
on the sprint board.

After that, it's simply a matter of starting a task and moving it to Doing,
actually doing the task, and when it's done, moving it to Done and picking up
the next one. And when all tasks of a story are done, the user story can be
moved to Done in sprint (after creating a codereview for the Gatekeepers in
FogBugz), and you can continue on a new task. Easy as that!

There are a few other noteworthy things to point out here.

- People assign themselves to cards as soon as they pick up a case. If a case
  isn't started, it probably won't have anyone assigned to it (unless there's a
  specific specialization involved). This makes it easy to see what is started
  and what not.
- Some cards are not related to user stories. These are GTD cases. GTD stands 
  for Getting Things Done, and are cards needed to get a user story from a
  previous sprint to production. As we have a gatekeeper and staging workflow
  that often happens in the sprint(s) after the feature was built, it is
  essential to track this as well.
- Note the small FogBugz logo (the kiwi) on many cards? That's a link to
  FogBugz, which is automatically generated by Trello. There's no such thing for
  other bugtrackers, but it is fairly trivial to make one yourself using
  something like `Greasemonkey`_.
- It would be an option to make tasks checklist items of cards, and do
  everything like we do above. However, we felt like this hid important details,
  which would go against the whole flow of having a tool like Trello. It might
  work for you however, so I did want to mention the option.

Backlogs
--------

We have three engineering teams, so we need three backlogs as well. One such
backlog boards can be seen below.

.. image:: |filename|/images/trello/backlog-board.png
    :align: center
    :alt: Backlog board

As you can see, it is quite straightforward. There's a Backlog list, containing
the stories that are up next, and there is a list for each sprint to be able to
keep an easy overview of what was done in which sprint.

For epics, we use checklists in Trello to group stories together. In that way,
the epic can stay on top of the backlog while its individual stories are
selected from the checklist and moved into the sprint. This works well in the
case that you work on a single epic but also want to work on smaller, unrelated
stories and features, as you can then prioritize the functionality (which the
epic encompasses) instead of fragments of a feature.

Burndown
--------

The biggest advantage and simultaneous disadvantage of Trello is that it does
one thing and does it well. This means that if you ever want to do something
else, such as generating a burndown, you will have to do it yourself. So, we
did.

Fortunately, Trello has an excellent `REST API <https://trello.com/docs/>`_,
which made it not so difficult to build a simple burndown application, as can be
seen below.

<< INSERT IMG HERE >>

To be able to generate this burndown however, you need a convention in how to
figure out how large a task is. Notice how in the sprint board above every task
has a number of "k" between brackets? That's the size of the task, and used to
generate the burndown with.

Thanks to the fact that we track everything based on tasks, and because our
tasks are as a rule no larger than 4 knots, our burndown is enormously detailed
and fine-grained, and as such gives you a very realistic view of what the
progress of each team is right now.

FogBugz
-------

Another thing that Trello misses is a way of tracking hours. There is a Chrome
extension to allow time tracking in Trello using `Harvest`_, but the thing is we
don't use Harvest, we use Fogbugz. So we developed a simple synchronization
tool for that, which we sadly haven't open sourced yet.

What it does is it looks at the tasks a member has in the "Doing" column, finds the
case corresponding to that task, and sets the user in FogBugz as working on that
case (using its `less than awesome API
<http://help.fogcreek.com/8202/xml-api>`_). It's not ideal, but it works for us.

Closing thoughts
================

So that's in a nutshell how we use Trello for visualizing our work. There are
many other tools out there of course that do the same as our solution does.
However, I personally haven't found one that I liked as much, and that allowed
the same flexibility, as what we have right now. Many tools that I found for
example don't allow you to generate a burndown of your tasks, only of your
user stories, which in my opinion is a serious limitation.

If you do have a tool that you can recommend, we are definitely open for
suggestions however. Custom tooling is nice, but you also have to maintain it,
so we're always on the lookout for an off the shelve solution. So if you know
something, please shoot me an email or leave a comment.

Oh and there is of course a Chrome plugin called `Scrum for Trello`_. When we
looked at it, it sadly wasn't very mature yet, but it does look pretty good now.
Give it a go!

.. External references:
.. _FogBugz: http://www.fogbugz.com/
.. _Fog Creek: http://www.fogcreek.com/
.. _Trello: http://trello.com/
.. _plugins: http://www.fogcreek.com/fogbugz/plugins/
.. _Greasemonkey: http://www.greasespot.net/
.. _Harvest: https://www.getharvest.com/trello/
.. _Scrum for Trello: https://chrome.google.com/webstore/detail/scrum-for-trello/jdbcdblgjdpmfninkoogcfpnkjmndgje?hl=en
.. _Kanban plugin: http://www.fogcreek.com/fogbugz/plugins/plugin.aspx?ixPlugin=15

