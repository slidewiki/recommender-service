import recommender


def get_store_titles_descriptions(rec):
    all_decks_ids, all_decks_titles, all_decks_descriptions, all_data_dict = rec.get_all_decks_ids_pagination()
    rec.store_dict(all_data_dict, "deckid_title_descrip")


if __name__ == "__main__":
    rec = recommender.RecommenderSystem()
    get_store_titles_descriptions(rec)