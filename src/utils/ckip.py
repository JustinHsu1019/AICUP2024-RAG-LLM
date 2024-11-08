from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger


ws_driver = CkipWordSegmenter(model="albert-base")
pos_driver = CkipPosTagger(model="albert-base")


def clean(sentence_ws, sentence_pos):
    short_sentence = []
    stop_pos = set(["Nep", "Nh", "Nb"])
    for word_ws, word_pos in zip(sentence_ws, sentence_pos):
        is_N_or_V = word_pos.startswith("V") or word_pos.startswith("N")
        is_not_stop_pos = word_pos not in stop_pos
        is_not_one_charactor = not (len(word_ws) == 1)
        if is_N_or_V and is_not_stop_pos and is_not_one_charactor:
            short_sentence.append(f"{word_ws}")
    return " ".join(short_sentence)
