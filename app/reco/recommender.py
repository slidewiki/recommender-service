import numpy as np
import requests
import json
from scipy import linalg, dot
import sklearn.metrics
import time
import sys
import math

from app import settings


# consider forks and sub-decks (not attached)

# item profiles
# user activity
# matrix userId x deckId (0 or 1 if rated/visited/etc)
# user profile creation
# similarity = recommendation


class RecommenderSystem(object):
    def __init__(self):
        print('Recommender object created')

    def get_all_decks_ids_pagination(self):
        all_decks_ids = []
        all_data_dict = {}
        names_dict = {}

        page = 1
        page_size = 1000
        more_pages = True

        base_url = settings.SERVICE_URL_DECK
        url = base_url + "/decks?rootsOnly=false&idOnly=false&status=public&sort=id&page=" + str(
            page) + "&pageSize=" + str(page_size)
        # consider using rootsOnly=true
        while more_pages:
            print('Getting decks and info. Requesting {}'.format(url))
            try:
                r = requests.get(url)
                try:
                    if r.status_code == 200:
                        result_json = r.json()
                        if result_json['_meta']['links'].get('next', 0) != 0:
                            url = base_url + result_json['_meta']['links']['next']
                        else:
                            more_pages = False

                        if len(result_json['items']) > 0:
                            for item in result_json['items']:
                                all_decks_ids.append(item['_id'])
                                first_slide, date, author_id, author = "", "", "", ""
                                if item.get('firstSlide', 0) != 0:
                                    first_slide = item['firstSlide']
                                if item.get('lastUpdate', 0) != 0:
                                    date = item['lastUpdate']
                                if item.get('owner', 0) != 0:
                                    author_id = item['owner']
                                    names_dict, author = self.get_display_name_or_user_name(names_dict, author_id)
                                all_data_dict[item['_id']] = {'id': item['_id'], 'title': item['title'],
                                                              'description': item['description'],
                                                              'firstSlide': first_slide,
                                                              'date': date,
                                                              'authorId': author_id,
                                                              'author': author}
                    else:
                        print(url + " returned status code = " + str(r.status_code))
                except KeyError:
                    print("Unexpected json response url= " + url)
            except requests.exceptions.SSLError:
                print("Unexpected error:", sys.exc_info()[0])

        return all_decks_ids, all_data_dict

    @staticmethod
    def get_display_name_or_user_name(names_dict, user_id):
        if user_id in names_dict:
            return names_dict, names_dict[user_id]
        base_url = settings.SERVICE_URL_USER
        url = base_url + '/user/' + str(user_id)
        try:
            r = requests.get(url)
            if r.status_code == 200:
                try:
                    result_json = r.json()
                    if 'displayName' in result_json and result_json['displayName']:
                        names_dict[user_id] = result_json['displayName']
                        return names_dict, result_json['displayName']
                    elif 'username' in result_json and result_json['username']:
                        names_dict[user_id] = result_json['username']
                        return names_dict, result_json['username']
                    return names_dict, ''
                except KeyError:
                    print("Unexpected json response url= " + url)
                    return names_dict, ''
            else:
                print(url + " returned status code = " + str(r.status_code))
                return names_dict, ''
        except requests.exceptions.SSLError:
            print("Unexpected error:", sys.exc_info()[0])
            return names_dict, ''

    @staticmethod
    def get_decks_user(user_id):
        decks_ids = []

        page = 1
        page_size = 1000
        more_pages = True

        base_url = settings.SERVICE_URL_DECK
        url = base_url + "/decks?user=" + str(user_id) + "&rootsOnly=false&idOnly=false&sort=id&page=" + str(
            page) + "&pageSize=" + str(page_size)

        while more_pages:
            try:
                r = requests.get(url)
                if r.status_code == 200:
                    try:
                        result_json = r.json()
                        if result_json['_meta']['links'].get('next', 0) != 0:
                            url = base_url + result_json['_meta']['links']['next']
                        else:
                            more_pages = False

                        if len(result_json['items']) > 0:
                            for item in result_json['items']:
                                decks_ids.append(item['_id'])
                    except KeyError:
                        print("Unexpected json response url= " + url)
                else:
                    print(url + " returned status code = " + str(r.status_code))
            except requests.exceptions.SSLError:
                print("Unexpected error:", sys.exc_info()[0])

        return decks_ids

    @staticmethod
    def get_deck_nlp(deck_id):
        print("retrieving NLP from deck=" + str(deck_id))

        perform_title_boost = "true"
        title_boost_with_fixed_factor = -1
        title_boost_limit_to_frequency_of_most_frequent_word = "true"
        min_frequency_of_term_or_entity_to_be_considered = 2
        apply_min_frequency_of_term_only_after_title_boost = "true"
        min_char_length_for_tag = 3
        max_number_of_words = 4
        min_docs_language_dependent = 50
        url = settings.SERVICE_URL_NLP + '/nlp/calculateTfidfValues/'

        r = None
        try:
            r = requests.get(url + str(deck_id) +
                             "?performTitleBoost=" + str(perform_title_boost) +
                             "&titleBoostWithFixedFactor=" + str(title_boost_with_fixed_factor) +
                             "&titleBoostlimitToFrequencyOfMostFrequentWord=" + str(
                title_boost_limit_to_frequency_of_most_frequent_word) +
                             "&minFrequencyOfTermOrEntityToBeConsidered=" + str(
                min_frequency_of_term_or_entity_to_be_considered) +
                             "&applyMinFrequencyOfTermOnlyAfterTitleBoost=" + str(
                apply_min_frequency_of_term_only_after_title_boost) +
                             "&minCharLengthForTag=" + str(min_char_length_for_tag) +
                             "&maxNumberOfWords=" + str(max_number_of_words) +
                             "&tfidfMinDocsToPerformLanguageDependent=" + str(min_docs_language_dependent))
        except requests.exceptions.SSLError:
            print("Unexpected error:", sys.exc_info()[0])
            return [], []

        if r.status_code != 200:
            print(url + " for deck_id=" + str(deck_id) + " returned status code = " + str(r.status_code))
            return [], []

        # "TFIDF_tokens_languagedependent"
        # "TFIDF_NER_languagedependent" #Named Entity Recognition (NER)
        # "TFIDF_DBPediaSpotlight_URI_languagedependent"
        #
        # TFIDF_tokens_notlanguagedependent

        result_json = r.json()
        tokens = []
        values_normalized = []
        try:
            if 'tfidfResult' not in result_json:
                print("empty NLP")
                return tokens, values_normalized

            if result_json['tfidfResult']['tfidfValuesWereCalculatedLanguageDependent']:

                if 'TFIDF_tokens_languagedependent' in result_json['tfidfResult']['tfidfMap']:
                    tokens_language_dependent = result_json['tfidfResult']['tfidfMap']['TFIDF_tokens_languagedependent']
                    for key, element in tokens_language_dependent.items():
                        tokens.append(key)
                        values_normalized.append(element)
                if 'TFIDF_NER_languagedependent' in result_json['tfidfResult']['tfidfMap']:
                    tokens_NER = result_json['tfidfResult']['tfidfMap']['TFIDF_NER_languagedependent']
                    for key, element in tokens_NER.items():
                        tokens.append(key)
                        values_normalized.append(element)
                if 'TFIDF_DBPediaSpotlight_URI_languagedependent' in result_json['tfidfResult']['tfidfMap']:
                    tokens_DBPedia = result_json['tfidfResult']['tfidfMap'][
                        'TFIDF_DBPediaSpotlight_URI_languagedependent']
                    for key, element in tokens_DBPedia.items():
                        tokens.append(key)
                        values_normalized.append(element)
            else:
                if 'TFIDF_tokens_notlanguagedependent' in result_json['tfidfResult']['tfidfMap']:
                    tokens_not_language_dependent = result_json['tfidfResult']['tfidfMap'][
                        'TFIDF_tokens_notlanguagedependent']
                    for key, element in tokens_not_language_dependent.items():
                        tokens.append(key)
                        values_normalized.append(element)
                if 'TFIDF_NER_notlanguagedependent' in result_json['tfidfResult']['tfidfMap']:
                    tokens_NER = result_json['tfidfResult']['tfidfMap']['TFIDF_NER_notlanguagedependent']
                    for key, element in tokens_NER.items():
                        tokens.append(key)
                        values_normalized.append(element)
                if 'TFIDF_DBPediaSpotlight_URI_notlanguagedependent' in result_json['tfidfResult']['tfidfMap']:
                    tokens_DBPedia = result_json['tfidfResult']['tfidfMap'][
                        'TFIDF_DBPediaSpotlight_URI_notlanguagedependent']
                    for key, element in tokens_DBPedia.items():
                        tokens.append(key)
                        values_normalized.append(element)

        except KeyError:
            print("Empty deck. No tokens available", sys.exc_info()[0])

        return tokens, values_normalized

    @staticmethod
    def get_deck_language(deck_id):
        perform_title_boost = "true"
        title_boost_with_fixed_factor = -1
        title_boost_limit_to_frequency_of_most_frequent_word = "true"
        min_frequency_of_term_or_entity_to_be_considered = 2
        apply_min_frequency_of_term_only_after_title_boost = "true"
        min_char_length_for_tag = 3
        max_number_of_words = 4
        min_docs_language_dependent = 50
        url = settings.SERVICE_URL_NLP + '/nlp/calculateTfidfValues/'
        try:
            r = requests.get(url + str(deck_id) +
                             "?performTitleBoost=" + str(perform_title_boost) +
                             "&titleBoostWithFixedFactor=" + str(title_boost_with_fixed_factor) +
                             "&titleBoostlimitToFrequencyOfMostFrequentWord=" + str(
                title_boost_limit_to_frequency_of_most_frequent_word) +
                             "&minFrequencyOfTermOrEntityToBeConsidered=" + str(
                min_frequency_of_term_or_entity_to_be_considered) +
                             "&applyMinFrequencyOfTermOnlyAfterTitleBoost=" + str(
                apply_min_frequency_of_term_only_after_title_boost) +
                             "&minCharLengthForTag=" + str(min_char_length_for_tag) +
                             "&maxNumberOfWords=" + str(max_number_of_words) +
                             "&tfidfMinDocsToPerformLanguageDependent=" + str(min_docs_language_dependent))

            if r.status_code == 200:
                result_json = r.json()
                try:
                    if len(result_json['tfidfResult']) == 0:
                        print("********* empty")
                        return []
                    language = result_json['tfidfResult']['language']
                    decks_given_language = result_json['tfidfResult']['numberOfDecksInPlatformWithGivenLanguage']

                    print("deck=" + str(deck_id) + " language: " + language + " " + str(decks_given_language))

                    return language, decks_given_language

                except KeyError:
                    print("Empty deck. No tokens available")
        except requests.exceptions.SSLError:
            print("Unexpected error:", sys.exc_info()[0])

        return None, None

    def get_all_decks_nlp_terms(self, deck_ids):
        all_decks_terms_and_values = {}
        all_terms = {}
        non_empty_nor_error_decks = 0
        empty_or_error_decks = 0
        used_deck_ids = []
        for deck_id in deck_ids:
            terms, values_normalized = self.get_deck_nlp(deck_id)
            if len(terms) > 0:
                all_decks_terms_and_values[deck_id] = {}
                non_empty_nor_error_decks = non_empty_nor_error_decks + 1
                used_deck_ids.append(deck_id)
                i = 0
                for term in terms:
                    occurrences = all_terms.get(term, 0)
                    occurrences = occurrences + 1
                    all_terms.update({term: occurrences})

                    all_decks_terms_and_values[deck_id][term] = values_normalized[i]

                    i += 1

            else:
                empty_or_error_decks = empty_or_error_decks + 1

        print("Retrieved data from " + str(non_empty_nor_error_decks) + " decks out of " + str(len(deck_ids)))
        print(str(len(all_terms)) + " terms")

        return all_decks_terms_and_values, all_terms, used_deck_ids

    @staticmethod
    def select_top_terms(all_terms, n_top):

        if len(all_terms) <= int(float(n_top)):
            return all_terms
        keys = []
        vals = []

        for k, v in all_terms.items():
            keys.append(k)
            vals.append(v)

        a = np.array(vals)

        indexes = np.argpartition(a, -n_top)[-n_top:]
        term_keys = [keys[index] for index in indexes]

        top_terms = {}
        for key, value in all_terms.items():
            if key in term_keys:
                top_terms[key] = value

        return top_terms

    @staticmethod
    def build_tfidf_matrix(all_decks_terms_and_values, all_terms):
        # matrix of N decks x M terms
        matrix = np.zeros((len(all_decks_terms_and_values), len(all_terms)))
        i = 0
        all_terms_positions = {}
        for key, value in all_terms.items():
            all_terms_positions[key] = i
            i += 1

        row = 0
        for deck_id in all_decks_terms_and_values:
            for term in all_decks_terms_and_values.get(deck_id):
                if term in all_terms:
                    term_id = all_terms_positions[term]
                    matrix[row][term_id] = all_decks_terms_and_values.get(deck_id).get(term)
            row += 1
        return matrix

    @staticmethod
    def get_user_activities_from_deck(deck_id):
        print("retrieving user activities from deck=" + str(deck_id))
        activities = {}
        likes, downloads = 0, 0
        url = settings.SERVICE_URL_ACTIVITIES + '/activities/deck/'
        try:
            r = requests.get(url + str(deck_id))
        except requests.exceptions.SSLError:
            print("Unexpected error:", sys.exc_info()[0])
        if r.status_code == 200:
            try:
                result_json = r.json()
                for activity in result_json['items']:
                    user_id = activity['user_id']
                    if user_id not in activities:
                        activities[user_id] = {deck_id: None}
                    if activity['activity_type'] == 'react':
                        likes += 1
                    if activity['activity_type'] == 'download':
                        downloads += 1

            except KeyError:
                print("Unexpected json response", sys.exc_info()[0])
        else:
            print(url + " returned status code = " + str(r.status_code))

        return activities, likes, downloads

    def get_all_users_activities_from_decks(self, deck_ids):
        all_activities = {}
        likes_downloads = {}
        for deck_id in deck_ids:
            acts, likes, downloads = self.get_user_activities_from_deck(deck_id)
            likes_downloads[deck_id] = {'likes': likes, 'downloads': downloads}
            for user_id in acts.keys():

                if user_id not in all_activities:
                    all_activities[user_id] = {deck_id: None}
                else:
                    all_activities[user_id].update({deck_id: None})

        return all_activities, all_activities.keys(), likes_downloads

    @staticmethod
    def build_user_activity_matrix(all_activities, user_ids, deck_ids):
        # matrix  userId  x deckId(0 or 1 if rated / visited / etc)

        # user -> deck
        matrix = np.zeros((len(user_ids), len(deck_ids)))

        i = 0
        all_user_ids_positions = {}
        for key, value in all_activities.items():
            all_user_ids_positions[key] = i
            i += 1

        j = 0
        all_deck_ids_positions = {}
        real_deck_ids = {}
        for key in deck_ids:
            all_deck_ids_positions[key] = j
            real_deck_ids[j] = key
            j += 1

        for user_id in all_activities:
            row = all_user_ids_positions[user_id]
            for deck_id in all_activities.get(user_id):
                column = all_deck_ids_positions[deck_id]

                matrix[row][column] = 1

        return matrix, all_user_ids_positions, real_deck_ids

    @staticmethod
    def cosine_similarity(features1, features2):
        dot_product, acum1, acum2 = 0, 0, 0
        for index, feature in enumerate(features1):
            if feature > 0:
                acum1 += feature * feature
                if features2[index] > 0:
                    dot_product += feature * features2[index]
            if features2[index] > 0:
                acum2 += features2[index] * features2[index]
        acum1 = math.sqrt(acum1)
        acum2 = math.sqrt(acum2)
        acum_product = acum1 * acum2
        cosine_similarity = 0
        if acum_product > 0:
            cosine_similarity = dot_product / acum_product
        return cosine_similarity

    def calculate_decks_similarity(self, matrix_tfidf, deck_ids):
        similarity_matrix = np.zeros((len(deck_ids), len(deck_ids)))

        all_deck_ids_positions = {}
        real_deck_ids = {}
        for index, key in enumerate(deck_ids):
            all_deck_ids_positions[key] = index
            real_deck_ids[index] = key

            for j in range(index + 1, len(deck_ids)):
                if index != j:
                    similarity = self.cosine_similarity(matrix_tfidf[index], matrix_tfidf[j])
                    similarity_matrix[index][j] = similarity
                    similarity_matrix[j][index] = similarity
        print("shape similarity matrix: " + str(similarity_matrix.shape))
        return similarity_matrix, all_deck_ids_positions, real_deck_ids

    @staticmethod
    def user_profile_creation(rating_matrix, item_prof_matrix):

        user_profile = dot(rating_matrix, item_prof_matrix) / linalg.norm(rating_matrix) / linalg.norm(item_prof_matrix)

        similarity = sklearn.metrics.pairwise.cosine_similarity(user_profile, item_prof_matrix, dense_output=True)

        return similarity

    @staticmethod
    def calculate_data_content_tfidfmatrix(self, deck_ids, max_features):
        start = time.time()
        all_decks_nlp_terms, all_terms, used_deck_ids = self.get_all_decks_nlp_terms(deck_ids)
        print(str(time.time() - start) + " get NLP terms elapsed time (seconds)")

        start = time.time()
        top_terms = self.select_top_terms(all_terms, max_features)
        print(str(time.time() - start) + " get top terms elapsed time (seconds)")

        start = time.time()
        matrix_tfidf = self.build_tfidf_matrix(all_decks_nlp_terms, top_terms)
        print(str(time.time() - start) + " build matrix elapsed time (seconds)")

        print("shape matrix tfidf: " + str(matrix_tfidf.shape))

        return matrix_tfidf, used_deck_ids

    @staticmethod
    def calculate_data_recommendation_user(self, deck_ids, max_features, file_name_suffix):

        matrix_tfidf, used_deck_ids = self.calculate_data_content_tfidfmatrix(self, deck_ids, max_features)

        start = time.time()
        all_users_activities, user_ids, likes_downloads = self.get_all_users_activities_from_decks(used_deck_ids)
        self.store_dict(likes_downloads, "./data/likes_downloads")
        print(str(time.time() - start) + " get user activities elapsed time (seconds)")

        start = time.time()
        matrix_user_activities, user_ids_positions, real_deck_ids = self.build_user_activity_matrix(
            all_users_activities,
            user_ids, used_deck_ids)
        print(matrix_user_activities)
        print(str(time.time() - start) + " build matrix user activities elapsed time (seconds)")
        print("shape matrix user activities: " + str(matrix_user_activities.shape))

        start = time.time()
        similarity = self.user_profile_creation(matrix_user_activities, matrix_tfidf)
        print(str(time.time() - start) + " user profile creation elapsed time (seconds)")

        self.store_matrix(similarity, './data/similarity' + file_name_suffix)
        self.store_dict(user_ids_positions, './data/user_ids_positions' + file_name_suffix)
        self.store_dict(real_deck_ids, './data/real_deck_ids' + file_name_suffix)

    @staticmethod
    def calculate_data_recommendation_deck(self, deck_ids, max_features, file_name_suffix):

        matrix_tfidf, used_deck_ids = self.calculate_data_content_tfidfmatrix(self, deck_ids, max_features)
        start = time.time()
        similarity, deck_ids_positions, real_deck_ids = self.calculate_decks_similarity(matrix_tfidf,
                                                                                        used_deck_ids)
        print(str(time.time() - start) + " similarity deck2deck matrix creation elapsed time (seconds)")
        self.store_matrix(similarity, './data/similarityContent' + file_name_suffix)
        self.store_dict(deck_ids_positions, './data/deck_ids_positionsContent' + file_name_suffix)
        self.store_dict(real_deck_ids, './data/real_deck_idsContent' + file_name_suffix)

    @staticmethod
    def calculate_data_recommendation_all(self, deck_ids, max_features, file_name_suffix):
        # common data: matrix_tfidf
        matrix_tfidf, used_deck_ids = self.calculate_data_content_tfidfmatrix(self, deck_ids, max_features)

        # DECK recommendation, a.k.a. only content recommendation
        start = time.time()
        similarity, deck_ids_positions, real_deck_ids = self.calculate_decks_similarity(matrix_tfidf,
                                                                                        used_deck_ids)
        print(str(time.time() - start) + " similarity deck2deck matrix creation elapsed time (seconds)")
        self.store_matrix(similarity, './data/similarityContent' + file_name_suffix)
        self.store_dict(deck_ids_positions, './data/deck_ids_positionsContent' + file_name_suffix)
        self.store_dict(real_deck_ids, './data/real_deck_idsContent' + file_name_suffix)

        # USER recommendation
        # get user activities for user recommendation
        start = time.time()
        all_users_activities, user_ids, likes_downloads = self.get_all_users_activities_from_decks(used_deck_ids)
        self.store_dict(likes_downloads, "./data/likes_downloads")
        print(str(time.time() - start) + " get user activities elapsed time (seconds)")

        matrix_user_activities, user_ids_positions, real_deck_ids = self.build_user_activity_matrix(
            all_users_activities,
            user_ids, used_deck_ids)
        print("shape matrix user activities: " + str(matrix_user_activities.shape))

        similarity = self.user_profile_creation(matrix_user_activities, matrix_tfidf)
        self.store_matrix(similarity, './data/similarity' + file_name_suffix)
        self.store_dict(user_ids_positions, './data/user_ids_positions' + file_name_suffix)
        self.store_dict(real_deck_ids, './data/real_deck_ids' + file_name_suffix)

    @staticmethod
    def user_recommendation(similarity, user_ids_positions, real_deck_ids, user_id, number_recom, user_deck_ids):

        user_id_position = user_ids_positions[str(user_id)]

        max_recom = number_recom + len(user_deck_ids)
        if len(real_deck_ids) < max_recom:
            max_recom = len(real_deck_ids)

        # get the N indexes with max similarity (unsorted)
        items_indexes = np.argpartition(similarity[user_id_position], -max_recom)[-max_recom:]
        # sort indexes by its similarity (lower to higher)
        items_indexes = items_indexes[np.argsort(similarity[user_id_position][items_indexes])]
        # reverse sort (higher to lower)
        items_indexes = items_indexes[::-1]

        recommended_deck_ids = []
        reco_values = []
        cont = 0
        for ind in items_indexes:
            recommended_deck_id = real_deck_ids[str(ind)]
            if recommended_deck_id not in user_deck_ids:
                recommended_deck_ids.append(recommended_deck_id)
                reco_values.append(similarity[user_id_position][ind])
                cont += 1
                if cont == number_recom:
                    break

        return recommended_deck_ids, reco_values

    @staticmethod
    def deck_recommendation(similarity, deck_ids_positions, real_deck_ids, deck_id, number_recom):

        deck_id_position = deck_ids_positions[str(deck_id)]

        max_recom = number_recom + 1
        if len(real_deck_ids) < max_recom:
            max_recom = len(real_deck_ids)

        # get the N indexes with max similarity (unsorted)
        items_indexes = np.argpartition(similarity[deck_id_position], -max_recom)[-max_recom:]
        # sort indexes by its similarity (lower to higher)
        items_indexes = items_indexes[np.argsort(similarity[deck_id_position][items_indexes])]
        # reverse sort (higher to lower)
        items_indexes = items_indexes[::-1]

        recommended_deck_ids = []
        reco_values = []
        cont = 0
        for ind in items_indexes:
            recommended_deck_id = real_deck_ids[str(ind)]
            if recommended_deck_id != deck_id:
                recommended_deck_ids.append(recommended_deck_id)
                reco_values.append(similarity[deck_id_position][ind])
                cont += 1
                if cont == number_recom:
                    break

        return recommended_deck_ids, reco_values

    @staticmethod
    def user_recommendation_from_storage(self, user_id, number_reco, file_name_suffix):

        similarity = self.load_matrix('./data/similarity' + file_name_suffix)
        user_ids_positions = self.load_dict('./data/user_ids_positions' + file_name_suffix)
        real_deck_ids = self.load_dict('./data/real_deck_ids' + file_name_suffix)

        # estimated time 0.5s
        user_deck_ids = self.get_decks_user(user_id)

        items_indexes, reco_values = self.user_recommendation(similarity, user_ids_positions, real_deck_ids, user_id,
                                                              number_reco, user_deck_ids)

        print("Recommended decks for user_id " + str(user_id) + ":")
        print(items_indexes)
        print(reco_values)

        return items_indexes, reco_values

    @staticmethod
    def deck_recommendation_from_storage(self, deck_id, number_reco, file_name_suffix):

        similarity = self.load_matrix('./data/similarityContent' + file_name_suffix)
        deck_ids_positions = self.load_dict('./data/deck_ids_positionsContent' + file_name_suffix)
        real_deck_ids = self.load_dict('./data/real_deck_idsContent' + file_name_suffix)

        items_indexes, reco_values = self.deck_recommendation(similarity, deck_ids_positions, real_deck_ids,
                                                              deck_id, number_reco)

        print("Recommended decks for deck_id " + str(deck_id) + ":")
        print(items_indexes)
        print(reco_values)

        return items_indexes, reco_values

    @staticmethod
    def store_matrix(matrix, name):
        np.save(name, matrix)

    @staticmethod
    def load_matrix(name):
        matrix = np.load(name + '.npy')
        return matrix

    @staticmethod
    def store_dict(my_dict, name):
        with open(name + '.json', 'w') as f:
            json.dump(my_dict, f)

    @staticmethod
    def load_dict(name):
        with open(name + '.json') as f:
            my_dict = json.load(f)
        return my_dict
