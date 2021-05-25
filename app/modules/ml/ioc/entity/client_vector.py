import string


class ClientVector:
    id: string
    vector: dict

    def __init__(self, id, vector: dict):
        self.id = id
        self.vector = vector
