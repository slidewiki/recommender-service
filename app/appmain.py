import logging.config
import os
import settings
from flask import Flask, Blueprint, request
from flask_restplus import Api, Resource, fields
import sys

sys.path.append("/")

from app.reco import recommender

app = Flask(__name__)
logging_conf_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../logging.conf'))
logging.config.fileConfig(logging_conf_path)
log = logging.getLogger(__name__)


def configure_app(flask_app):
    flask_app.config['SERVER_NAME'] = settings.FLASK_SERVER_NAME
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP


def initialize_app(flask_app):
    configure_app(flask_app)

    blueprint = Blueprint('reco', __name__)

    api = Api(version='Beta', title='Recommender Service',
              description='Recommendation of SlideWiki decks', doc='/documentation')

    @api.errorhandler
    def default_error_handler(e):
        message = 'An unhandled exception occurred.'
        log.exception(message)

        if not settings.FLASK_DEBUG:
            return {'message': message}, 500

    api.init_app(blueprint)

    recommendation_user_namespace = api.namespace('userRecommendation',
                                                  description='Operations related to user recommendation')

    recommendation_deck_namespace = api.namespace('deckRecommendation',
                                                  description='Operations related to deck recommendation')

    deck = api.model('Recommended deck', {
        'id': fields.Integer(readOnly=True, required=True, description='The unique identifier of a deck'),
        'title': fields.String(description='Deck title'),
        'description': fields.String(description='Deck description'),
        'value': fields.Float(description='Recommendation value'),
    })

    @recommendation_user_namespace.route('/<int:user_id>')
    @api.response(404, 'User id not found.')
    @api.doc(params={'user_id': 'The unique identifier of a user'})
    @api.doc(params={'numberReco': 'Number of desired recommendations'})
    class UserRecommendation(Resource):
        @api.marshal_list_with(deck)
        def get(self, user_id, number_reco=5):
            """
            Returns list of recommended decks for a user.
            """
            if 'numberReco' in request.args:
                try:
                    number_reco = int(request.args['numberReco'])
                except ValueError:
                    pass

            file_name_suffix = "Full1500"
            rec = recommender.RecommenderSystem()

            # check valid user_id
            user_ids_positions = rec.load_dict("user_ids_positions" + file_name_suffix)
            if str(user_id) not in user_ids_positions:
                return None, 404

            recommended_decks, reco_values = rec.get_recommendation_from_storage(rec, user_id, number_reco,
                                                                                 file_name_suffix)
            all_data_dict = rec.load_dict("deckid_title_descrip")
            recommended_decks_list_dict = []
            cont = 0
            for i in recommended_decks:
                recommended_deck = all_data_dict[str(i)]
                recommended_deck['value'] = reco_values[cont]
                recommended_decks_list_dict.append(recommended_deck)
                cont += 1

            return recommended_decks_list_dict

    @recommendation_deck_namespace.route('/<int:deck_id>')
    @api.response(404, 'Deck id not found.')
    @api.doc(params={'deck_id': 'The unique identifier of a deck'})
    @api.doc(params={'numberReco': 'Number of desired recommendations'})
    class DeckRecommendation(Resource):

        @api.marshal_list_with(deck)
        def get(self, deck_id, number_reco=5):
            """
            Returns list of recommended decks for a deck (only content-based).
            """
            if 'numberReco' in request.args:
                try:
                    number_reco = int(request.args['numberReco'])
                except ValueError:
                    pass
            file_name_suffix = "Full1500"
            rec = recommender.RecommenderSystem()

            # check valid deck_id
            deck_ids_positions = rec.load_dict("deck_ids_positionsContent" + file_name_suffix)
            if str(deck_id) not in deck_ids_positions:
                return None, 404

            recommended_decks, reco_values = rec.get_recommendation_from_storage_only_content(rec, deck_id, number_reco,
                                                                                              file_name_suffix)
            all_data_dict = rec.load_dict("deckid_title_descrip")
            recommended_decks_list_dict = []
            cont = 0
            for i in recommended_decks:
                recommended_deck = all_data_dict[str(i)]
                recommended_deck['value'] = reco_values[cont]
                recommended_decks_list_dict.append(recommended_deck)
                cont += 1

            return recommended_decks_list_dict

    api.add_namespace(recommendation_user_namespace)
    api.add_namespace(recommendation_deck_namespace)

    flask_app.register_blueprint(blueprint)


def main():
    initialize_app(app)
    log.info('>>>>> Starting server at http://{}/ <<<<<'.format(app.config['SERVER_NAME']))
    app.run(host='0.0.0.0', port=80, debug=settings.FLASK_DEBUG, use_reloader=False)


if __name__ == "__main__":
    main()
