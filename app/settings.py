# Flask settings
PORT = 8000
FLASK_SERVER_NAME = 'localhost:' + str(PORT)  # localhost: or recommenderservice.experimental.slidewiki.org:
FLASK_DEBUG = False  # Do not use debug mode in production

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

