import pickle


class Saveable:

    def save(self, path: str):
        file = open(path, 'wb')
        pickle.dump(self, file)
