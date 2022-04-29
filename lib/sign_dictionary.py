import pickle

# class dict_item:
#     def __init__(self, mocap_source_file, video_reference_file, sl_annotator, video_time_stamp, mocap_time_stamp, mocap_cleaner, signer, annot_default, annot_left_hand, annot_right_hand, codified_meaning):

def load_dictionary(path):
    with open(path, 'rb') as f:
        loaded = pickle.load(f)
    return loaded

def save_dictionary(dictionary, path):
    with open(path, 'wb') as f:
        pickle.dump(dictionary, f)