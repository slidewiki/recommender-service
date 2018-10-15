# Recommender service #

[![License](https://img.shields.io/badge/License-MPL%202.0-green.svg)](https://github.com/slidewiki/microservice-template/blob/master/LICENSE)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)


Recommender service using a RESTful API based on Flask-RESTPlus.
It is a personalized content-based recommender of decks for any user of SlideWiki based on the activity of the user.
It also offers only content-based recommendations of decks given a deck (id) as input.
The features of the decks considered are the contents of the deck itself using tf-idf.

### How to install and run with docker

1. git clone https://github.com/slidewiki/recommender-service
2. cd recommender-service/
3. (if needed) Change corresponding server name (with port) in FLASK_SERVER_NAME and services URLs at app/settings.py 
4. (sudo) docker build -t test-recommender-service .
5. (sudo) docker run -it --rm -p 8000:8000 test-recommender-service 
6. The service will be available at http://localhost:8000 with the documentation available at http://localhost:8000/documentation

### How to install and run without docker

1. git clone https://github.com/slidewiki/recommender-service
2. cd recommender-service/
3. Install python 3.6 or higher (Ubuntu 17.10, Ubuntu 18.04, and above, come with Python 3.6 by default)
4. Install python3 package installer (if not already installed): 'sudo apt install python3-pip'
5. Install libraries of 'requirements.txt' with 'pip3 install -r requirements.txt'
6. Change corresponding server name (with port) in FLASK_SERVER_NAME and services URLs at app/settings.py 
7. Setup/install the application: 'sudo python3 setup.py install'
8. Run the server: 'python3 app/appmain.py'
9. The service will be available at localhost:PORT with the documentation available at localhost:PORT/documentation

### How to update the contents of recommendation

1. cd recommender-service/
2. (if needed) Change MAX_FEATURES and/or FILE_NAME_SUFFIX at app/settings.py to consider a different number of features to consider by the recommender. 
Note that if these values are changed, the recommender will not work until a complete app/reco/update.py process is made. 
3. python3 app/reco/update.py 
Note that this process will take proportional time to complete depending on the number of decks and the responding time of the different used services, mainly activity service and nlp service.