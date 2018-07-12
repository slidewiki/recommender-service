import numpy as np
import requests
import json
from scipy import linalg, dot
import sklearn.metrics
import time
import sys


# consider LANGUAGE:
# TOTAL:3868, UNKNOWN 2252, en 1343, es 87, de 56, da 42, cy 24, el 18, nl 9, et 9, af 7,
# fa 5, sv 4, bg 4, it 3, pt 2, is 2, mt 2, pl 2, ar 2, ru 2, hr 1, mk 1, ms 1, sw 1, so 1,
# consider forks and sub-decks (not attached)

# item profiles
# user activity
# matrix userId x deckId (0 or 1 if rated/visited/etc)
# user profile creation
# similarity = recommendation


class RecommenderSystem(object):
    def __init__(self):
        print()

    @staticmethod
    def get_all_decks_ids_pagination():
        all_decks_ids = []
        all_decks_titles = []
        all_decks_descriptions = []
        all_data_dict = {}

        page = 1
        page_size = 1000
        more_pages = True

        base_url = 'https://deckservice.experimental.slidewiki.org'
        url = base_url + "/decks?rootsOnly=false&idOnly=false&sort=id&page=" + str(page) + "&pageSize=" + str(page_size)
        # TODO consider using rootsOnly=true
        while more_pages:
            r = requests.get(url)

            try:
                result_json = r.json()
                if result_json['_meta']['links'].get('next', 0) != 0:
                    url = base_url + result_json['_meta']['links']['next']
                else:
                    more_pages = False

                if len(result_json['items']) > 0:
                    for item in result_json['items']:
                        all_decks_ids.append(item['_id'])
                        all_decks_titles.append(item['title'])
                        all_decks_descriptions.append(item['description'])
                        all_data_dict[item['_id']] = {'id': item['_id'], 'title': item['title'],
                                                      'description': item['description']}
            except:
                print("Unexpected json response")

        return all_decks_ids, all_decks_titles, all_decks_descriptions, all_data_dict

    @staticmethod
    def get_decks_user(user_id):
        decks_ids = []

        page = 1
        page_size = 1000
        more_pages = True

        base_url = 'https://deckservice.experimental.slidewiki.org'
        url = base_url + "/decks?user=" + str(user_id) + "&rootsOnly=false&idOnly=false&sort=id&page=" + str(
            page) + "&pageSize=" + str(page_size)

        while more_pages:
            r = requests.get(url)

            try:
                result_json = r.json()
                if result_json['_meta']['links'].get('next', 0) != 0:
                    url = base_url + result_json['_meta']['links']['next']
                else:
                    more_pages = False

                if len(result_json['items']) > 0:
                    for item in result_json['items']:
                        decks_ids.append(item['_id'])
            except:
                print("Unexpected json response")

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
        url = 'https://nlpservice.experimental.slidewiki.org/nlp/calculateTfidfValues/'

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
        except:
            print("Unexpected error:", sys.exc_info()[0])
        try:
            result_json = r.json()
        except:
            print("Unexpected json response")
            return [], []

        # "TFIDF_tokens_languagedependent"
        # "TFIDF_NER_languagedependent" #Named Entity Recognition (NER)
        # "TFIDF_DBPediaSpotlight_URI_languagedependent"
        #
        # TFIDF_tokens_notlanguagedependent

        tokens = []
        valuesNormalized = []
        try:
            if len(result_json['tfidfResult']) == 0:
                print("********* empty")
                return tokens, valuesNormalized

            tokens_language_dependent = result_json['tfidfResult']['tfidfMap']['TFIDF_tokens_languagedependent']
            for key, element in tokens_language_dependent.items():
                tokens.append(key)
                valuesNormalized.append(element)

            tokens_NER = result_json['tfidfResult']['tfidfMap']['TFIDF_NER_languagedependent']
            for key, element in tokens_NER.items():
                tokens.append(key)
                valuesNormalized.append(element)

            tokens_DBPedia = result_json['tfidfResult']['tfidfMap']['TFIDF_DBPediaSpotlight_URI_languagedependent']
            for key, element in tokens_DBPedia.items():
                tokens.append(key)
                valuesNormalized.append(element)

        except:
            print("Empty deck. No tokens available")

        return tokens, valuesNormalized

    @staticmethod
    def get_deck_language(deck_id):
        # print("retrieving NLP from deck=" + str(deck_id))

        perform_title_boost = "true"
        title_boost_with_fixed_factor = -1
        title_boost_limit_to_frequency_of_most_frequent_word = "true"
        min_frequency_of_term_or_entity_to_be_considered = 2
        apply_min_frequency_of_term_only_after_title_boost = "true"
        min_char_length_for_tag = 3
        max_number_of_words = 4
        min_docs_language_dependent = 50
        url = 'https://nlpservice.experimental.slidewiki.org/nlp/calculateTfidfValues/'

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

        try:
            result_json = r.json()
        except:
            print("Unexpected json response")
            return None, None

        try:
            if len(result_json['tfidfResult']) == 0:
                print("********* empty")
                return []
            language = result_json['tfidfResult']['language']
            decks_given_language = result_json['tfidfResult']['numberOfDecksInPlatformWithGivenLanguage']

            print("deck=" + str(deck_id) + " language: " + language + " " + str(decks_given_language))

            return language, decks_given_language

        except:
            print("Empty deck. No tokens available")

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
        url = 'https://activitiesservice.experimental.slidewiki.org/activities/deck/'
        try:
            r = requests.get(url + str(deck_id))
        except:
            print("Unexpected error:", sys.exc_info()[0])
        try:
            result_json = r.json()
            for activity in result_json['items']:
                user_id = activity['user_id']
                if user_id not in activities:
                    activities[user_id] = {deck_id: None}
        except:
            print("Unexpected json response")

        return activities

    def get_all_users_activities_from_decks(self, deck_ids):
        all_activities = {}
        for deck_id in deck_ids:
            acts = self.get_user_activities_from_deck(deck_id)
            for user_id in acts.keys():

                if user_id not in all_activities:
                    all_activities[user_id] = {deck_id: None}
                else:
                    all_activities[user_id].update({deck_id: None})

        return all_activities, all_activities.keys()

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
    def build_deck2deck_matrix(deck_ids):
        # matrix  deckId  x deckId (0 or 1 if rated / visited / etc)

        matrix = np.ones((len(deck_ids), len(deck_ids)), dtype=int)

        j = 0
        all_deck_ids_positions = {}
        real_deck_ids = {}
        for key in deck_ids:
            all_deck_ids_positions[key] = j
            real_deck_ids[j] = key
            j += 1

        for i in range(0, len(deck_ids)):
            matrix[i][i] = 0

        return matrix, all_deck_ids_positions, real_deck_ids

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
    def calculate_data_recommendation(self, deck_ids, max_features, file_name_suffix):

        matrix_tfidf, used_deck_ids = self.calculate_data_content_tfidfmatrix(self, deck_ids, max_features)

        start = time.time()
        all_users_activities, user_ids = self.get_all_users_activities_from_decks(used_deck_ids)
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

        self.store_matrix(similarity, 'similarity' + file_name_suffix)
        self.store_dict(user_ids_positions, 'user_ids_positions' + file_name_suffix)
        self.store_dict(real_deck_ids, 'real_deck_ids' + file_name_suffix)

    @staticmethod
    def calculate_data_recommendation_only_content(self, deck_ids, max_features, file_name_suffix):

        matrix_tfidf, used_deck_ids = self.calculate_data_content_tfidfmatrix(self, deck_ids, max_features)

        matrix_deck, deck_ids_positions, real_deck_ids = self.build_deck2deck_matrix(used_deck_ids)

        deck_profile = dot(matrix_deck, matrix_tfidf) / linalg.norm(matrix_deck) / linalg.norm(matrix_tfidf)

        similarity = sklearn.metrics.pairwise.cosine_similarity(deck_profile, matrix_tfidf, dense_output=True)

        self.store_matrix(similarity, 'similarityContent' + file_name_suffix)
        self.store_dict(deck_ids_positions, 'deck_ids_positionsContent' + file_name_suffix)
        self.store_dict(real_deck_ids, 'real_deck_idsContent' + file_name_suffix)

    @staticmethod
    def recommendation(similarity, user_ids_positions, real_deck_ids, user_id, number_recom, user_deck_ids):

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
    def recommendation_only_content(similarity, deck_ids_positions, real_deck_ids, deck_id, number_recom):

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
    def get_recommendation_from_storage(self, user_id, number_reco, file_name_suffix):

        similarity = self.load_matrix('similarity' + file_name_suffix)
        user_ids_positions = self.load_dict('user_ids_positions' + file_name_suffix)
        real_deck_ids = self.load_dict('real_deck_ids' + file_name_suffix)

        # estimated time 0.5s
        user_deck_ids = self.get_decks_user(user_id)

        items_indexes, reco_values = self.recommendation(similarity, user_ids_positions, real_deck_ids, user_id,
                                                         number_reco, user_deck_ids)

        print("Recommended decks for user_id " + str(user_id) + ":")
        print(items_indexes)
        print(reco_values)

        return items_indexes, reco_values

    @staticmethod
    def get_recommendation_from_storage_only_content(self, deck_id, number_reco, file_name_suffix):

        similarity = self.load_matrix('similarityContent' + file_name_suffix)
        deck_ids_positions = self.load_dict('deck_ids_positionsContent' + file_name_suffix)
        real_deck_ids = self.load_dict('real_deck_idsContent' + file_name_suffix)

        items_indexes, reco_values = self.recommendation_only_content(similarity, deck_ids_positions, real_deck_ids,
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