:title: How we use Trello and custom tooling to streamline our development process
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
easily extensible with `plugins`_. Back then, everyone got assigned a case at
the start of the sprint, and you worked on your case until it was finished. When
it was finished, you could ask for another case. Cases came from a single
prioritized list, and were assigned by the team leader based on FTE's available
and his estimations of hours of work.

So what exactly was wrong with this approach? Many things, but what I want to
focus on now is that there was no way for anyone to get an insight in the
progress of any individual case, let alone the sprint itself.

Sure, you could go to an individual case in FogBugz and see how many hours were
registered on it, but that only helps you if you live in a fairy tale world
where an hour registered directly correlates with an hour less work to be done.
You could also of course talk with the engineer working on the case, but as he
didn't make the estimate and because there was no structure for creating tasks,
he often didn't really know what was left to do. As you can imagine, this led to
many issues towards the end of a sprint, with cases not being finished and
no-one knowing what was going on.

Evolution
=========

This approach evolved quite a bit before arriving to our current solution. One
of the improvements was the introduction of the `Kanban plugin`_ in FogBugz,
which allowed people to see in which sprint which case would be done. Definitely
an improvement, but not yet enough.

Another was to simply use wall stickies. While this was nice and tangible, it
also had its downsides. A burndown had to be drawn by hand (what are we,
peasants?), and there was a bit of a barrier (however tiny) to get up, walk over
to the board and create a card if you need one. This caused many fires (and
other work) to be undocumented and as such invisible, which made controlling the
sprint even harder.

And of course, by using stickies there was no log of past sprints, a huge
downside as well. And it didn't scale. And stickies started falling of the wall.
You get my point.

Enter Trello
============

To quote from their site: "Trello makes it easy to organize anything with
anyone". Luckily for us, it does indeed. We now use it for our sprint boards so
that teams can register their planned work and progress, as well as for our
backlog boards. I'll now go into some more detail on these boards.

Sprint board
------------

A typical sprint board of one of our teams looks something like this:

.. image:: |filename|/images/trello/sprint-board.png
    :align: center
    :alt: Sprint board

Let's go through the columns (or lists in Trello's terminology).

- **User stories**: The user stories committed for this sprint. Each of these has
  a case number, written before its nameof it, and an estimate, written behind
  it between brackets. You can read "knots" basically as `story points`_.
- **User stories - Done in sprint**: The user stories that fulfill the Definition
  of Done, at least for within the sprint. In our case, user stories often
  aren't deployed during a sprint, so there's a separate Definition of Done for
  that.
- **To Do**: This column contains the *tasks* of the user stories that still
  have to be done. The tasks are not really linked to user stories (Trello does
  not provide such functionality between cards), but by using the same case
  number and the same color, we can visually distinguish them quite easily.
- **Doing**: These are tasks that are currently in progress.
- **Done**: All tasks that are completed will end up here.
- **Fires**: All fires encountered in this sprint. We often use a placeholder to
  keep a buffer for unexpected work.
- **Fires Done**: A fire that was completed will end up here.

During the sprint planning, each team creates cards for the user stories and the
tasks on the sprint board of that sprint. Everything on the sprint board is part
of the commitment, so this is automatically generated.

Important to note is that the team itself is in full charge of this board. Not
the team leader, not the SCRUM master, but the team. More complicated or
cumbersome tools are often managed by a single person, which is actually a bad
thing as the responsibility of owning and administrating the work (and
commitment) is then not correctly distributed. Thanks to Trello being so
accessible and easy to use, it is no problem to have the team be the owner of
this as well.

After sprint planning, it's simply a matter of starting a task and moving it to
Doing, actually doing the task, and when it's done, moving it to Done and
picking up the next one. When all tasks of a story are done, the user story can
be moved to Done in sprint (after creating a codereview for the Gatekeepers in
FogBugz), and you can start work on another task. Easy as that!

There are a few other things that are worthy of pointing out:

- People assign themselves to cards as soon as they start work on a story. If a
  story isn't started yet, it probably won't have anyone assigned to it (unless
  there's a specific specialization involved). This makes it easy to see what is
  started and what not.
- Some cards are not related to user stories. These are GTD cases. GTD stands
  for Getting Things Done, and are cards needed to get a user story which was
  completed in a previous sprint to production. As we have a gatekeeper and
  staging workflow that usually happens in the sprint(s) after the feature was
  built, it is essential to track this as well.
- Note the small FogBugz logo (the kiwi) on many cards? That's a link to
  FogBugz, which is automatically generated by Trello. There's no such thing for
  other bug trackers, but it is fairly trivial to make one yourself using
  something like `Greasemonkey`_.
- It's also an option to create tasks as checklist items on user story cards,
  and work on tasks from there. However, we felt like this obscures important
  details, which for us goes against the idea of using a tool like Trello. It
  might work for you however, so I did want to mention the option.

Backlogs
--------

We have three engineering teams, so we need three backlogs as well. One such
backlog board can be seen below.

.. image:: |filename|/images/trello/backlog-board.png
    :align: center
    :alt: Backlog board

As you can see, it is quite straightforward. There's a Backlog list, containing
the user stories that are up next, and there is a list for each sprint, to be
able to keep an easy overview of what was done in which sprint.

For epics, we use checklists in Trello to group related stories together. In
that way, the epic can stay on top of the backlog while its individual stories
are selected from the checklist and moved into the sprint. This works well in
the case that you work on a single epic but also want to work on smaller,
unrelated stories and features next to it, as you can then prioritize the entire
functionality (which the epic encompasses) instead of just fragments of it.

Custom tooling
==============

The biggest advantage and simultaneous disadvantage of Trello is that it does
just one thing and does it well. This means that if you ever want to do
something else, such as generating a burndown chart, you will have to do it
yourself. So, we did.

Burndown
--------

Fortunately, Trello has an excellent `REST API`_, which makes it quite easy to
get the data needed for a simple burndown. We started off with a `burndown chart
in Google Docs`_, which is a nice and lightweight way to start using Trello for
your sprints. It turned out we needed a bit more flexibility however, so we
developed our own burndown application.

.. image:: |filename|/images/trello/burndown.png
    :align: center
    :alt: Custom burndown chart

To be able to generate a burndown using Trello however, you need a way to set
the size of a task, which we do by convention. Notice how in the sprint board
shown above every task has a number of "k" between brackets, so like (2k)?
That's our convention for setting the size of the task, which is of course
trivially parsed.

Thanks to the fact that we track everything based on tasks, and because our
tasks are as a rule no larger than 4 knots, our burndown is enormously detailed
and fine-grained, and as such gives you a very realistic view of what the
progress of each team is on every given moment.

FogBugz
-------

Another thing that Trello doesn't have is time tracking. There is a Chrome
extension to allow time tracking in Trello using `Harvest`_, but the thing is we
don't use Harvest; we use Fogbugz. So we developed a simple synchronization tool
for that, which we sadly haven't open sourced yet.

What it does is it periodically looks at the task a member has in the "Doing"
column, finds the case corresponding to that task in FogBugz, and starts
registering hours for that user on that case (using `FogBugz's less than awesome
API`_). It's not ideal, but it works for us, and saves our engineers the hassle
of having to do double administration.

Of course, being resourceful engineers, we integrated this information then
again with our burndown chart, so that we could display what every engineer is
working on right now next to the burndown chart, together with the progress of
the case. Magic!

.. image:: |filename|/images/trello/workon.png
    :align: center
    :alt: Displaying of who works on what case

Closing thoughts
================

So that's in a nutshell how we use Trello for our sprints. We've been using it
for our sprint boards for nearly two years now, and it definitely has stood the
test of time. We've been using it for other things as well, such as for project
management, as Kanban board for our Operational IT team, and for storing code
snippets. The fact that there is Google Apps integration is quite a bonus there
for us as well.

Now it has to be mentioned that there are many other tools out there that
attempt to solve all of our problems in a single tool. This would of course be
better, so that we wouldn't have to develop and maintain our custom tooling.
However, I personally haven't found one that I liked as much, and that allowed
the same flexibility, as what we have right now. For example, many tools that I
found don't allow you to generate a burndown based on your tasks, only of your
user stories, which in my opinion is a serious limitation. If you do have a tool
that you can recommend,  please shoot me an email or leave a comment.

Oh and there is of course a Chrome plugin called `Scrum for Trello`_. When we
looked at it, it sadly wasn't very mature yet and it didn't fit our needs, but
it does look pretty good now. Someone also pointed out `Plus for Trello`_ to me
which I didn't know about before, but it looks promising as well. Give it a go!

And don't forget to check out the `taco game`_.

.. External references:
.. _FogBugz: http://www.fogbugz.com/
.. _Fog Creek: http://www.fogcreek.com/
.. _Trello: http://trello.com/
.. _plugins: http://www.fogcreek.com/fogbugz/plugins/
.. _story points: https://www.scrumalliance.org/community/articles/2014/january/a-practical-guide-story-points-based-estimation.aspx
.. _Greasemonkey: http://www.greasespot.net/
.. _REST API: https://trello.com/docs/
.. _Harvest: https://www.getharvest.com/trello/
.. _Fogbugz's less than awesome API: http://help.fogcreek.com/8202/xml-api
.. _Scrum for Trello: https://chrome.google.com/webstore/detail/scrum-for-trello/jdbcdblgjdpmfninkoogcfpnkjmndgje?hl=en
.. _Kanban plugin: http://www.fogcreek.com/fogbugz/plugins/plugin.aspx?ixPlugin=15
.. _burndown chart in Google Docs: http://echobehind.wordpress.com/2012/06/28/create-your-own-burndown-chart-using-trello-api-and-google-apps-script/
.. _Plus for Trello: https://chrome.google.com/webstore/detail/plus-for-trello/gjjpophepkbhejnglcmkdnncmaanojkf/related?hl=en
.. _taco game: https://trello.com/taco-game
