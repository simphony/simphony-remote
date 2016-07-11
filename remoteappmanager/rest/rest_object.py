import uuid

from tornado import gen


class RESTObject:
    @classmethod
    @gen.coroutine
    def create(cls, representation):
        raise NotImplementedError()

    @classmethod
    @gen.coroutine
    def retrieve(cls, identifier):
        raise NotImplementedError()

    @classmethod
    @gen.coroutine
    def update(cls, identifier, representation):
        raise NotImplementedError()

    @classmethod
    def delete(cls, identifier):
        raise NotImplementedError()

    @classmethod
    @gen.coroutine
    def exists(cls, identifier):
        try:
            cls.retrieve(identifier)
        except Exception:
            return False

        return True

    @classmethod
    @gen.coroutine
    def items(cls):
        return []
