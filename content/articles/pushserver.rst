:title: pushserver
:date: 2015-02-09 13:01
:summary: Settings configuration system based on entry points of setuptools
:category: Open source
:author: Anatoly Bubenkov
:slug: articles/pushserver
:tags: open source, python, redis-cluster, push notifications, server-sent events, SSE, html5, pub/sub

.. contents::

Introduction
------------

Paylogic constantly works on improving the user experience of our frontoffice. One of the important things when you
buy a ticket, is the availability counter. The availability counter shows the user how many tickets
(for a certain venue) are available for purchase.
Paylogic Frontoffice - is one of our products which is a web application to sell the tickets for the merchant events.
It is simple, powerful and flexible to satisfy our clients needs. Visually it's done as a wizard with dynamic set of
steps: tickets, overview, payment and so on.
At the moment the Paylogic frontoffice does not show ticket availability: if the ticket locking went
fine users are simply forwarded to the next step. If there's not enough tickets available, you're
informed about that. This leads to the need of the constant request-response football between the user and the backend
just to figure out the maximum number of tickets the user can buy.
`pushserver <https://github.com/paylogic/pushserver>`_ which enables backend services to send real-time events
to web clients.
This article describes the motivation, technology in brief and implementation details of the ``pushserver``.


User experience
---------------

Paylogic constantly improves the user experience of our products. Frontoffice
(the service which does the actual sale) is the most important among them. Basic flow of the ticket sale
contains such steps (simplified):

* Get the list of tickets (ticket types)
* Select ticket(s) quantities
* Check out the basket

The second step becomes difficult for the user, if the number of tickets is limited (which is usually the case).
The user, to make a right choice, needs to know how many tickets are available.
But how does he know, and more importantly, when, that availability was changed?
This problem can be solved in several ways:

Update the availability when the choice is made, if there's not enough, there will be an user error with availability counter.
    This is probably the simplest option to implement, but from the user perspective most unnatural and unintuitive, as
    he doesn't expect there is only 1 ticket left, if the select box with the quantity allows him to select 10.

Update the availability once per certain amount of time, e.g. every second.
    This is more user-friendly. But if we'll keep the period very short to emulate real-time updates, then it will be
    problematic for the server to handle, as it will look like real DDOS attack from many clients (during the peak
    sales we have thousands and thousands of concurrent connections).

Update the availability at the time it changes.
    If there's no change, why bother client's browser with the old information?
    Also the server is not attacked anymore.


But how to implement this?
--------------------------

So we need a way to send updates from the server to the client, without the need of explicit request for the new info
from the client side.
There's a nice `answer <http://stackoverflow.com/questions/11077857/what-are-long-polling-websockets-server-sent-events-sse-and-comet/12855533#12855533>`_
which describes the basics.

So we have options:

`Long polling <http://en.wikipedia.org/wiki/Push_technology#Long_polling>`_
    Browser support is 100%. That's probably the strongest side of this technique. But reconnection and state restore is
    completely the problem of the implementation, there's no helpers provided by the standard as there's no such:
    it's just normal HTTP, which ends in some long period, and for the browser it's like one big document.

`Websockets <http://en.wikipedia.org/wiki/WebSocket>`_
    `Browser support <http://caniuse.com/websockets>`_ is not 100% but is very good, but is it what's needed? It is, but
    it gives us much more that enough: it's two-way communication channel. But we don't really need it for our problem.
    Most if not all updates are coming ``from`` the server. Updates from the client are normal requests (XMLHttpRequest)
    if there is a need. Also websockets are not HTTP but TCP (HTTP is used only during the handshake)
    so it requires much more hassle from the OPIT side, as they will need to set up the balancing on the TCP level.

`Server sent events (SSE) <http://en.wikipedia.org/wiki/Server-sent_events>`_
    Browser support is `not that bad <http://caniuse.com/eventsource>`_, and increasing constantly. It's one-way
    communication channel, but with very useful features provided by the browser: state restore on connection failure (
    browser sends the last event ID it received since disconnection), automatic reconnection and a very easy javascript
    interface.

Those options provide possibilities we need but they are not equal, so SSE seems to be the most optimal.
As we use Python a lot, we've looked around for some existing solutions which implement SSE server-side, we've found
`flask sse <https://github.com/DazWorrall/flask-sse>`_, which seemed what we need.

Flask-sse uses redis `pubsub <http://redis.io/topics/pubsub>`_ as a backend for broadcasting the events from the server.
Using `redis-cluster <http://redis.io/topics/cluster-spec>`_ which is currently in beta, but
`will be released soon <https://twitter.com/antirez/status/478425814040854528>`_ (and actually already used in
production as reported by Salvatore Sanfilippo) allows us to have high available, scalable web service.


Use-case
--------

Possible use-case can be drawn as following:


.. image:: |filename|/images/pushserver/diagram-user-perspective.png
    :align: center
    :alt: pushserver use-case from the user perspective

Actor changes some data on the backend via normal request to the backend. All users receive the broadcasted message
from the backend via long-lasting channel for server-sent events.

And the deployment can look like:

.. image:: |filename|/images/pushserver/diagram-deployment.png
    :align: center
    :alt: pushserver use-case possible deployment schema


Sending events to a push server from your app
---------------------------------------------

::

    from flask.ext.sse import send_event

    send_event('myevent', {"message": "Hello!"}, channel='mychannel')


Client side
-----------

On the client side you just need a javascipt handler function which will be called when a new message is pushed
from the server.

::

    var source = new EventSource('/stream?channel=mychannel');
    source.addEventListener('myevent', function (event) {
         alert(event.data);
    };

Server-Sent Events are `supported <http://caniuse.com/#feat=eventsource>`_ by recent Firefox,
Chrome and Safari browsers.
Internet Explorer does not yet support Server-Sent Events, so there are two recommended Polyfills
to support older browsers:

* `EventSource.js <https://github.com/remy/polyfills/blob/master/EventSource.js>`_
* `jquery.eventsource <https://github.com/rwldrn/jquery.eventsource>`_

Mobile browsers have limited support, so test carefully if it works for your target set of browsers.


Live demo
---------

Here is a small demo video of the potential of this technique: we use pushserver to update the ticket availability in
our frontoffice application, which is where users can buy the tickets. The left and right windows are operated by
different users and are completely independent. When ticket availability is changed by the action from the left
window's operator, the right window changes instantly, without the polling involved (you can see the network bar).

Simple frontoffice where you can only select the quantity of the ticket(s):

.. html::

    <video
        width='720' height='480' preload='none'
        controls src='/videos/pushserver-in-action.mov'
        poster='/images/pushserver/pushserver-in-action.png' />

More advanced example, where you can pick a seat:

.. html::

    <video
        width='720' height='480' preload='none' controls src='/videos/pushserver-seating-demo.mov'
        poster='/images/pushserver/pushserver-seating-demo.png' />


Future considerations for Paylogic
----------------------------------

We are considering to create a special stream API, where API users can listen to the events to get them instantly
instead of polling the state from time to time. This is especially important for the cases like result of the
payment processing, availability change, etc.
For now, it's more like an experiment for us, but it's a promising technology and we're eager to hear some feedback from
the developers who use our API if it will be useful for them to have the stream API.
