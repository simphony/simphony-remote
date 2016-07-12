from remoteappmanager.rest.resource import Resource
from tornado import gen


class Container(Resource):
    @gen.coroutine
    def create(self, representation):
        # This should create the container.
        # the representation should accept the application mapping id we
        # want to start
        pass

    @gen.coroutine
    def retrieve(self, identifier):
        # We should return the representation of the running container
        # with its current status
        pass


    @gen.coroutine
    def update(self, identifier, representation):
        # Used to change the status. We should be able to say status=stop.
        # and this will stop the container
        pass


    @gen.coroutine
    def delete(self, identifier):
        # This should stop the container. Maybe we should skip the status
        # modification, and just use delete to stop a container?
        pass

    @gen.coroutine
    def items(self):
        # We should return the list of containers we are currently
        # running.
        return []
