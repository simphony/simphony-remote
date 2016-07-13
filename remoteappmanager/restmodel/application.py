from remoteappmanager.rest.exceptions import NotFound
from remoteappmanager.rest.resource import Resource
from tornado import gen


class Application(Resource):
    @gen.coroutine
    def retrieve(self, identifier):
        apps = self.application.db.get_apps_for_user(
            self.current_user.account
        )

        # Convert the list of tuples in a dict
        apps_dict = {mapping_id: (app, policy)
                     for mapping_id, app, policy in apps}

        if identifier not in apps_dict:
            raise NotFound

        app, policy = apps_dict[identifier]
        representation = dict(
            image=app.image,
        )
        return representation

    @gen.coroutine
    def items(self):
        """Retrieves a dictionary containing the image and the associated
        container, if active, as values."""
        apps = self.application.db.get_apps_for_user(self.current_user.account)

        return [mapping_id for mapping_id, _, _ in apps]
