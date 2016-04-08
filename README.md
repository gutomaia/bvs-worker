bvs-worker
==========

This is a backend application for "Batman VS Superman Opinions", the goal here is to analyse tweets related to the movie and sumarize opinions using Alchemy API.

Disclaimer, this is a proof-of-concept using Bluemix platform and services.

How does it work
----------------

As said, this is just the backend application. It uses tweepy to fetch the tweets and it publishes and stores on a redis service. In the time between it also uses Alchemy sentiment API to gather if the opinion is positive/negative/neutral.

Messages published on Redis were listen by the frontend application and shared using SocketIO.


Async
-----

The receive of the tweet and the processing the request on alchemyapi are dealeded apart, what gives a better feedback for the user on interface. I choose to use a threadpool to process this after the tweet.

Services
--------

Project demands the use Redis and Alchemy API. Both were pretty simple to configure on Bluemix service.

Tests
-----

Coverage is low, and was only applied on most meaniful parts of the project.

Run
---

You will need credentials on Twitter and on Alchemy API, for a development environment, just rename the development.ini example filling the required vars. Then just type: "make" and then "make run".

When make was RUN on the first time, it downloads a custom python.mk receipe made by me on the makery project.


Engenieering trade-offs
-----------------------

As a proof-of-concept, some shortcuts were took. Example. It would make more sence if the whole API were presented in the backend application and the frontend were just a "app shell". However, just to simplify the integration, development enviroment and avoid the use of CORs, witch is not subject in this POC, those gaps were left on propose.

A huge improvement would be, kill the integration using "redis backend" and done it on the frontend using web standards. By killing backend integration I mean, not use Redis PubSub beetween applications to exchange data. Although this is common pattern and not a issue it self. Woulbe just a nice engeniering stand-off.

Reporting Issues
----------------

Pull requests and open issues were welcome.

License
-------

It's a standard MIT license, fell free to share.
