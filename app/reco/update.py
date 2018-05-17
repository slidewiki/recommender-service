import time
import recommender


def update_all_recommendations(rec):
    main_start = time.time()

    start = time.time()
    deck_ids, all_decks_titles, all_decks_descriptions, all_data_dict = rec.get_all_decks_ids_pagination()
    time_get_decks = time.time() - start
    print(str(time_get_decks) + " get deck ids elapsed time (seconds)")

    max_features = 1500
    file_name_suffix = 'Full' + str(max_features)

    start = time.time()
    rec.calculate_data_recommendation(rec, deck_ids, file_name_suffix, max_features)
    end = time.time()
    print(str(end - start) + " get data elapsed time (seconds)")

    main_end_time = time.time() - main_start
    print(str(main_end_time) + " TOTAL elapsed time (seconds)")


if __name__ == "__main__":
    rec = recommender.RecommenderSystem()
    update_all_recommendations(rec)

