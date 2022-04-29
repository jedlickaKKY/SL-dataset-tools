import pickle

def load_dictionary(path):
    with open(path, 'rb') as f:
        loaded = pickle.load(f)
    return loaded

def save_dictionary(dictionary, path):
    with open(path, 'wb') as f:
        pickle.dump(dictionary, f)