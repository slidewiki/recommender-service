# Flask settings
PORT = 8000
FLASK_SERVER_NAME = 'localhost:' + str(PORT)  # localhost: or recommenderservice.experimental.slidewiki.org:
FLASK_DEBUG = False  # Do not use debug mode in production

# Services URLs
DECK_SERVICE_URL = 'https://deckservice.experimental.slidewiki.org'
ACTIVITIES_SERVICE_URL = 'https://activitiesservice.experimental.slidewiki.org'
USER_SERVICE_URL = 'https://userservice.experimental.slidewiki.org'
NLP_SERVICE_URL = 'https://nlpservice.experimental.slidewiki.org'

# Recommender features
MAX_FEATURES = 2000
FILE_NAME_SUFFIX = 'Full' + str(MAX_FEATURES)

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

