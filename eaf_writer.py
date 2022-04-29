import pickle

if __name__ == '__main__':
    with open('anot.pkl', 'rb') as handle:
        b = pickle.load(handle)

    for i in b:
        print(i)
