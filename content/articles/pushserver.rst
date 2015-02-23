:title: pushserver
:date: 2015-02-09 13:01
:summary: Pub/sub server to broadcast real-time updates from the server to clients
:category: Open source
:author: Anatoly Bubenkov
:slug: articles/pushserver
:tags: open source, python, redis-cluster, push notifications, server-sent events, SSE, html5, pub/sub

.. contents::

Introduction
------------

Paylogic is constantly working to improve the user experience of it's ticketing platform. When buying a ticket, one of
the most important things to know is the amount of available tickets. The Paylogic Frontoffice is one of the products
Paylogic uses to allow event organizers to sell tickets for their events. It is a simple yet powerful and flexible web
application. The purchasing process is set up as a wizard with a dynamic set of steps: select tickets, order overview,
payment and so on. The availability counter shows the user how many tickets are still available for a certain event. At
the moment the Paylogic Frontoffice does not have a real-time indication of the ticket availability. The user selects
his tickets and pushes the "next" button. If all goes well the user is simply forwarded to the next step. If, however,
there are not enough tickets available to satisfy the users request, he is send back to the ticket selection step and
informed about this. This leads to a constant request-response football between the user and the backend just to figure
out the maximum number of tickets the user can buy. In comes the `pushserver <https://github.com/paylogic/pushserver>`_
which enables the backend services to send real-time events to the web clients. This article describes the motivation
and gives a brief overview of the technology and implementation details of a ``pushserver``.


User experience
---------------

Paylogic is constantly improving the user experience of it's' products. The Frontoffice being the most important among
them. The basic flow of the ticket sale can be simplified as the following steps:

* Get the list of available ticket types
* Select the requested ticket quantities
* Check out the basket

The second step becomes difficult for the user if the number of available tickets is limited. To allow the user to make
the right choice he needs to know how many tickets are still available. The question becomes: how does the user get to
know this, and more importantly, when. The user might be pondering over the available ticket types for a few minutes. At
the same time another user might come in and take some tickets. How does the first user know that the number of
available tickets was changed?

This problem can be solved in several ways:

Update the availability when the choice is made. 
    If after clicking the next button it turns out there are not enough tickets available, an error will be send
    to the user with the updated availability counter. This is probably the simplest option to implement. However, from
    the user's perspective this process is unnatural and unintuitive. The user doesn't expect that there is only 1
    ticket left if the select box allowed him to select
    10.

Update the availability on an interval, e.g. every 10 seconds.
    This is more user-friendly but if we take a very short period to emulate real-time updates, then this can be
    problematic for the server to handle. In essence it will look like DDOS attack, as during peak sales we have tens of
    thousands of users using the Frontoffice all at once.

Update the availability at the time it changes.
    If there's no change, why bother the client's browser with information it already knows? This also allows the
    servers to not get overloaded as it is no longer the browser but the pushserver who is deciding on the amount of
    traffic.


But how to implement this?
--------------------------

So we need a way to send updates from the server to the client without the need for the browser to explicitly request
the new information. There's a nice `answer
<http://stackoverflow.com/questions/11077857/what-are-long-polling-websockets-server-sent-events-sse-and-comet/12855533#12855533>`_
at Stack Overflow which describes the basic options for such a scheme.

There are a few options available:

`Long polling <http://en.wikipedia.org/wiki/Push_technology#Long_polling>`_
    Browser support is 100%. That's probably the only strong point of this technique. The problem of constantly
    reconnecting and state recovery is completely in the hands of the implementation. There are no helpers provided by
    any standard as there's no such thing. It really is just a normal HTTP request which takes a long time and to the
    browser it's just one big document.

`Websockets <http://en.wikipedia.org/wiki/WebSocket>`_
    `Browser support <http://caniuse.com/websockets>`_ is not 100% but is very good. Is it what's needed for our
    problem? It could fit very well but it gives us much more than we need. Websockets provide a two-way communication
    channel but we don't really need that for our problem. All updates are coming ``from`` the server. Updates from the
    client are done using normal requests (XMLHttpRequest or regular POST). Additionally websockets are not HTTP but raw
    TCP, HTTP is only used for the handshake. This means it requires much more hassle from the OPIT side as they will
    need to set up a raw TCP service next to the current web service.

`Server sent events (SSE) <http://en.wikipedia.org/wiki/Server-sent_events>`_
    Browser support is `not that bad <http://caniuse.com/eventsource>`_, and increasing constantly. Server sent events
    provide a one-way communication channel. However, this channel has some very useful features provided by the
    browser:
    * Automatic reconnect in case of a connection problem
    * State restoration on reconnect (the browser sends the last event ID it received before the disconnect)
    * A very easy javascript interface

Those options all provide the possibilities we need but they are not equal. SSE seems to be the most optimal for our use
case. As we use Python a lot, we've looked around for some existing solutions which implement SSE server-side. We've
found `flask sse <https://github.com/DazWorrall/flask-sse>`_, which seems to be exactly what we need.

Flask-sse uses Redis `pubsub <http://redis.io/topics/pubsub>`_ as a backend for broadcasting the events from the server.
It uses `redis-cluster <http://redis.io/topics/cluster-spec>`_ which is currently in beta, but `will be released soon
<http://antirez.com/news/79>`_ (and is actually already used in production as reported by Salvatore Sanfilippo).
Flask-sse on top of redis-cluster allows us to have a high available, scalable web service.


Use-case
--------

A possible use-case can be drawn as follows:


.. image:: |filename|/images/pushserver/diagram-user-perspective.png
    :align: center
    :alt: pushserver use-case from the user perspective

The actor changes some data on the backend via a normal request to the backend. All users receive the broadcasted
message from the backend via long-lasting channel for server-sent events.

The deployment may look like this:

.. image:: |filename|/images/pushserver/diagram-deployment.png
    :align: center
    :alt: pushserver use-case possible deployment schema


Sending events to a push server
-------------------------------

::

    from flask.ext.sse import send_event

    send_event('myevent', {"message": "Hello!"}, channel='mychannel')


Receiving events in the browser
-------------------------------

On the client side you just need a javascipt handler function which will be called when a new message is pushed from the
server.

::

    var source = new EventSource('/stream?channel=mychannel');
    source.addEventListener('myevent', function (event) {
         alert(event.data);
    };

Server-Sent Events are `supported <http://caniuse.com/#feat=eventsource>`_ by recent Firefox, Chrome and Safari
browsers. Internet Explorer does not yet support Server-Sent Events but there are two recommended Polyfills to support
IE and older browsers:

* `EventSource.js <https://github.com/remy/polyfills/blob/master/EventSource.js>`_
* `jquery.eventsource <https://github.com/rwldrn/jquery.eventsource>`_

Mobile browsers have limited support, so test carefully whether it works for your target set of browsers.


Live demo
---------

Here is a small demo video of the potential of this technique: we use pushserver to update the ticket availability in
our Frontoffice application. The left and right windows are operated by different users and are completely independent.
When the ticket availability is changed by an action from the left window's operator, the right window changes instantly
without any polling involved (you can see the network bar).

A simple Frontoffice where you can only select the quantity of tickets:

.. html::

    <video
        width='720' height='480' preload='none'
        controls src='/videos/pushserver-in-action.mov'
        poster='/images/pushserver/pushserver-in-action.png' />

A More advanced example where you can pick a seat:

.. html::

    <video
        width='720' height='480' preload='none' controls src='/videos/pushserver-seating-demo.mov'
        poster='/images/pushserver/pushserver-seating-demo.png' />


Future considerations for Paylogic
----------------------------------

We are considering creating a special stream API where API users can subscribe to events and get them instantly instead
of needing to poll the state from time to time. This is especially important for things like collecting the result of
payment processing, ticket availability changes, etc.

For now, Server sent events are more like an experiment for us, but it's a promising technology. We're eager to hear
some feedback from developers who use our API on whether it will be useful for them to have a stream API.
