import time
import recommender


def update_all_recommendations(rec):
    main_start = time.time()

    start = time.time()
    deck_ids, all_data_dict = rec.get_all_decks_ids_pagination()
    rec.store_dict(all_data_dict, "deckid_title_descrip")
    time_get_decks = time.time() - start
    print('{} obtained deck ids'.format(len(deck_ids)))
    print(str(time_get_decks) + " get deck ids elapsed time (seconds)")

    max_features = 1500
    file_name_suffix = 'Full' + str(max_features)

    start = time.time()
    rec.calculate_data_recommendation_all(rec, deck_ids, max_features, file_name_suffix)
    end = time.time()
    print(str(end - start) + " get data elapsed time (seconds)")

    main_end_time = time.time() - main_start
    print(str(main_end_time) + " TOTAL elapsed time (seconds)")


def update_user_recommendations(rec):
    main_start = time.time()

    start = time.time()
    deck_ids, all_data_dict = rec.get_all_decks_ids_pagination()
    rec.store_dict(all_data_dict, "deckid_title_descrip")
    time_get_decks = time.time() - start
    print('{} obtained deck ids'.format(len(deck_ids)))
    print(str(time_get_decks) + " get deck ids elapsed time (seconds)")

    max_features = 1500
    file_name_suffix = 'Full' + str(max_features)

    start = time.time()
    rec.calculate_data_recommendation_user(rec, deck_ids, max_features, file_name_suffix)
    end = time.time()
    print(str(end - start) + " get data elapsed time (seconds)")

    main_end_time = time.time() - main_start
    print(str(main_end_time) + " TOTAL elapsed time (seconds)")


def update_deck_recommendations(rec):
    main_start = time.time()

    start = time.time()
    deck_ids, all_data_dict = rec.get_all_decks_ids_pagination()
    rec.store_dict(all_data_dict, "deckid_title_descrip")
    time_get_decks = time.time() - start
    print('{} obtained deck ids'.format(len(deck_ids)))
    print(str(time_get_decks) + " get deck ids elapsed time (seconds)")

    max_features = 1500
    file_name_suffix = 'Full' + str(max_features)

    start = time.time()
    rec.calculate_data_recommendation_deck(rec, deck_ids, max_features, file_name_suffix)
    end = time.time()
    print(str(end - start) + " get data elapsed time (seconds)")

    main_end_time = time.time() - main_start
    print(str(main_end_time) + " TOTAL elapsed time (seconds)")


def update_subset_content_recommendations(rec):
    main_start = time.time()

    deck_ids = [1, 2, 3, 7, 10, 14, 183, 269, 292, 344, 475, 1071, 1091, 1092, 1095, 1200, 1202, 1203, 1235, 1236,
                1238, 1281, 1284, 1285, 1286, 1366, 1367, 1368, 1369, 1370, 1371, 1372, 1373, 1436, 1437, 1438, 1439,
                1441, 1442, 1443, 1444, 1445, 1446, 1447, 1465, 1468, 1469, 1470, 1471, 1472, 1473, 1474, 1475, 1476,
                1477, 1478, 1479, 1480, 1485, 1488, 1490, 1492, 1495, 1596, 1597, 1633, 1665, 1723, 1922, 1946, 2112,
                2118, 2124, 2137, 2178, 2225, 2287, 2322, 2345, 2347, 2518, 2521, 2522, 2523, 2544, 2545, 2546, 2547,
                2548, 2549, 2550, 2551, 2552, 2553, 2554, 2555, 2556, 2557, 2558]

    max_features = 1500
    file_name_suffix = 'Full' + str(max_features)

    start = time.time()
    rec.calculate_data_recommendation_deck(rec, deck_ids, max_features, file_name_suffix)
    end = time.time()
    print(str(end - start) + " get data elapsed time (seconds)")

    main_end_time = time.time() - main_start
    print(str(main_end_time) + " TOTAL elapsed time (seconds)")


if __name__ == "__main__":
    rec = recommender.RecommenderSystem()
    update_all_recommendations(rec)
    # update_subset_content_recommendations(rec)
