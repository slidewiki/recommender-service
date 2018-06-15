# Recommender service #
=============

[![Build Status](https://travis-ci.org/slidewiki/recommender-service.svg?branch=master)](https://travis-ci.org/slidewiki/recommender-service)
[![License](https://img.shields.io/badge/License-MPL%202.0-green.svg)](https://github.com/slidewiki/microservice-template/blob/master/LICENSE)
[![Language]](https://www.python.org/)


Recommender service using a RESTful API based on Flask-RESTPlus.
It is a personalized content-based recommender of decks for any user of SlideWiki based on the activity of the user.
The features of the decks considered are the contents of the deck itself using tf-idf.

### How to

1. git clone https://github.com/slidewiki/recommender-service
2. cd recommender-service/
3. docker build -t test-recommender-service .
4. docker run -it --rm -p 8880:3000 test-recommender-service
5. the service will be available at localhost:8880 with the documentation available at localhost:8880/documentation