class RESTObject:

    @classmethod
    def create(self):
        raise NotImplementedError()

    @classmethod
    def retrieve(self):
        raise NotImplementedError()

    @classmethod
    def update(self):
        raise NotImplementedError()

    @classmethod
    def delete(self):
        raise NotImplementedError()

    @classmethod
    def list(self):
        return []
