import os

# Flask settings
PORT = int(os.environ.get("APPLICATION_PORT", default="8000"))
FLASK_SERVER_NAME = os.environ.get("FLASK_SERVER_NAME", default=("localhost:" + str(PORT)))
FLASK_DEBUG = False  # Do not use debug mode in production

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

# Microservices Settings
SERVICE_URL_DECK = os.environ.get("SERVICE_URL_DECK", default="https://deckservice.experimental.slidewiki.org")
SERVICE_URL_USER = os.environ.get("SERVICE_URL_USER", default="https://userservice.experimental.slidewiki.org")
SERVICE_URL_ACTIVITIES = os.environ.get("SERVICE_URL_ACTIVITIES", default="https://activitiesservice.experimental.slidewiki.org")
SERVICE_URL_NLP = os.environ.get("SERVICE_URL_NLP", default="https://nlpservice.experimental.slidewiki.org")
