import logging.config
import os
import settings
from flask import Flask, Blueprint, request
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix

import sys

sys.path.append(".")

from app.reco import recommender

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
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

    api = Api(version='1.0', title='Recommender Service',
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
    recommendation_mixed_namespace = api.namespace('deckUserRecommendation',
                                                   description='Operations related to deck user recommendation')

    deck = api.model('Recommended deck', {
        'id': fields.Integer(readOnly=True, required=True, description='The unique identifier of a deck'),
        'title': fields.String(description='Deck title'),
        'description': fields.String(description='Deck description'),
        'firstSlide': fields.String(description='First Slide ID'),
        'authorId': fields.Integer(description='Author ID'),
        'author': fields.String(description='Author username'),
        'date': fields.String(description='Date of last update'),
        'likes': fields.Integer(description='Number of likes'),
        'downloads': fields.Integer(description='Number of downloads'),
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

            rec = recommender.RecommenderSystem()

            # check valid user_id
            user_ids_positions = rec.load_dict("./data/user_ids_positions" + settings.FILE_NAME_SUFFIX)
            if str(user_id) not in user_ids_positions:
                return None, 404

            recommended_decks, reco_values = rec.user_recommendation_from_storage(rec, user_id, number_reco,
                                                                                  settings.FILE_NAME_SUFFIX)
            all_data_dict = rec.load_dict("./data/deckid_title_descrip")
            likes_downloads = rec.load_dict("./data/likes_downloads")
            recommended_decks_list_dict = []
            cont = 0
            for i in recommended_decks:
                recommended_deck = all_data_dict[str(i)]
                recommended_deck['value'] = reco_values[cont]
                recommended_deck['likes'] = likes_downloads[str(i)]['likes']
                recommended_deck['downloads'] = likes_downloads[str(i)]['downloads']
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

            rec = recommender.RecommenderSystem()

            # check valid deck_id
            deck_ids_positions = rec.load_dict("./data/deck_ids_positionsContent" + settings.FILE_NAME_SUFFIX)
            if str(deck_id) not in deck_ids_positions:
                return None, 404

            recommended_decks, reco_values = rec.deck_recommendation_from_storage(rec, deck_id, number_reco,
                                                                                  settings.FILE_NAME_SUFFIX)

            all_data_dict = rec.load_dict("./data/deckid_title_descrip")
            likes_downloads = rec.load_dict("./data/likes_downloads")
            recommended_decks_list_dict = []
            cont = 0
            for i in recommended_decks:
                recommended_deck = all_data_dict[str(i)]
                recommended_deck['value'] = reco_values[cont]
                recommended_deck['likes'] = likes_downloads[str(i)]['likes']
                recommended_deck['downloads'] = likes_downloads[str(i)]['downloads']
                recommended_decks_list_dict.append(recommended_deck)
                cont += 1

            return recommended_decks_list_dict

    parser = api.parser()
    parser.add_argument('user_id', type=int, required=True, help='The unique identifier of a user')
    parser.add_argument('numberReco', type=int, help='Number of desired recommendations')

    @recommendation_mixed_namespace.route('/<int:deck_id>')
    @api.response(404, 'Deck id not found.')
    @api.response(405, 'User id not found.')
    @api.doc(params={'deck_id': 'The unique identifier of a deck'})
    class DeckUserRecommendation(Resource):
        @api.doc(parser=parser)
        @api.marshal_list_with(deck)
        def get(self, deck_id, number_reco=5):
            """
            Returns list of recommended decks for a deck (only content-based) and a user.
            """
            if 'deck_id' in request.args:
                try:
                    deck_id = int(request.args['deck_id'])
                except ValueError:
                    return None, 404
            if 'user_id' in request.args:
                try:
                    user_id = int(request.args['user_id'])
                except ValueError:
                    return None, 405
            if 'numberReco' in request.args:
                try:
                    number_reco = int(request.args['numberReco'])
                except ValueError:
                    pass

            rec = recommender.RecommenderSystem()

            # check valid deck_id
            deck_ids_positions = rec.load_dict("./data/deck_ids_positionsContent" + settings.FILE_NAME_SUFFIX)
            if str(deck_id) not in deck_ids_positions:
                return None, 404
            # check valid user_id
            user_ids_positions = rec.load_dict("./data/user_ids_positions" + settings.FILE_NAME_SUFFIX)
            if str(user_id) not in user_ids_positions:
                return None, 405

            recommended_decks_deck, reco_values_deck = rec.deck_recommendation_from_storage(rec, deck_id,
                                                                                            number_reco,
                                                                                            settings.FILE_NAME_SUFFIX)
            recommended_decks_user, reco_values_user = rec.user_recommendation_from_storage(rec, user_id, number_reco,
                                                                                            settings.FILE_NAME_SUFFIX)
            all_data_dict = rec.load_dict("./data/deckid_title_descrip")
            likes_downloads = rec.load_dict("./data/likes_downloads")
            recommended_decks_list_dict_deck = []
            cont = 0
            for i in recommended_decks_deck:
                recommended_deck = all_data_dict[str(i)]
                recommended_deck['value'] = reco_values_deck[cont]
                recommended_deck['likes'] = likes_downloads[str(i)]['likes']
                recommended_deck['downloads'] = likes_downloads[str(i)]['downloads']
                recommended_decks_list_dict_deck.append(recommended_deck)
                cont += 1
            cont = 0
            recommended_decks_list_dict_user = []
            for i in recommended_decks_user:
                recommended_deck = all_data_dict[str(i)]
                recommended_deck['value'] = reco_values_user[cont]
                recommended_deck['likes'] = likes_downloads[str(i)]['likes']
                recommended_deck['downloads'] = likes_downloads[str(i)]['downloads']
                recommended_decks_list_dict_user.append(recommended_deck)
                cont += 1

            recommended_decks_list_dict = []
            recommended_decks_ids = []
            deck_reco_count, user_reco_count, n_reco = 0, 0, 0

            intersection = [value for value in recommended_decks_deck if value in recommended_decks_user]
            for reco_deck_id in intersection:
                recommended_decks_ids.append(reco_deck_id)
                for i in range(0, len(recommended_decks_list_dict_deck)):
                    reco_deck = {}
                    if recommended_decks_list_dict_deck[i]['id'] == reco_deck_id:
                        reco_deck = recommended_decks_list_dict_deck[i]
                        break
                recommended_decks_list_dict.append(reco_deck)
                n_reco += 1

            cont = 0
            while n_reco < number_reco:
                if cont > len(recommended_decks_list_dict_deck) + len(recommended_decks_list_dict_user):
                    break
                cont += 1
                if deck_reco_count < len(recommended_decks_list_dict_deck) and \
                        recommended_decks_list_dict_deck[deck_reco_count]['id'] not in recommended_decks_ids:
                    recommended_decks_ids.append(recommended_decks_list_dict_deck[deck_reco_count]['id'])
                    recommended_decks_list_dict.append(recommended_decks_list_dict_deck[deck_reco_count])
                    n_reco += 1
                deck_reco_count += 1
                if user_reco_count < len(recommended_decks_list_dict_user) and \
                        recommended_decks_list_dict_user[user_reco_count]['id'] not in recommended_decks_ids and \
                        n_reco < number_reco:
                    recommended_decks_ids.append(recommended_decks_list_dict_user[user_reco_count]['id'])
                    recommended_decks_list_dict.append(recommended_decks_list_dict_user[user_reco_count])
                    n_reco += 1
                user_reco_count += 1

            return recommended_decks_list_dict

    api.add_namespace(recommendation_user_namespace)
    api.add_namespace(recommendation_deck_namespace)
    api.add_namespace(recommendation_mixed_namespace)

    flask_app.register_blueprint(blueprint)


def main():
    initialize_app(app)
    log.info('>>>>> Starting server at http://{}/ <<<<<'.format(app.config['SERVER_NAME']))
    app.run(host='0.0.0.0', port=settings.PORT, debug=settings.FLASK_DEBUG, use_reloader=False)


if __name__ == "__main__":
    main()
