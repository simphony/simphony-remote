from tornado import gen


class RESTObject:
    @gen.coroutine
    @classmethod
    def create(cls, representation):
        raise NotImplementedError()

    @gen.coroutine
    @classmethod
    def retrieve(cls, identifier):
        raise NotImplementedError()

    @gen.coroutine
    @classmethod
    def update(cls, identifier, representation):
        raise NotImplementedError()

    @gen.coroutine
    @classmethod
    def delete(cls, identifier):
        raise NotImplementedError()

    @gen.coroutine
    @classmethod
    def exists(cls, identifier):
        try:
            cls.retrieve(identifier)
        except Exception as e:
            return False

        return True

    @gen.coroutine
    @classmethod
    def list(cls):
        return []
