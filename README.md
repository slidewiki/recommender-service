# Recommender service #

[![License](https://img.shields.io/badge/License-MPL%202.0-green.svg)](https://github.com/slidewiki/microservice-template/blob/master/LICENSE)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)


Recommender service using a RESTful API based on Flask-RESTPlus.
It is a personalized content-based recommender of decks for any user of SlideWiki based on the activity of the user.
It also offers only content-based recommendations of decks given a deck (id) as input.
The features of the decks considered are the contents of the deck itself using tf-idf.

### How to

1. git clone https://github.com/slidewiki/recommender-service
2. cd recommender-service/
3. docker build -t test-recommender-service .
4. docker run -it --rm -p 8880:3000 test-recommender-service
5. the service will be available at localhost:8880 with the documentation available at localhost:8880/documentation

### How to without docker

1. git clone https://github.com/slidewiki/recommender-service
2. cd recommender-service/
3. Install python 3.6 or higher (Ubuntu 17.10, Ubuntu 18.04, and above, come with Python 3.6 by default)
4. Install python3 package installer (if not already installed): 'sudo apt install python3-pip'
5. Install libraries of 'requirements.txt' with 'pip3 install -r requirements.txt'
6. Change corresponding server name (with port) in FLASK_SERVER_NAME at app/settings.py
7. Setup/install the application: 'sudo python3 setup.py install'
8. Run the server: 'python3 app/appmain.py'