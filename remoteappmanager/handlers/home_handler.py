from tornado import gen, web

from remoteappmanager.handlers.base_handler import BaseHandler


class HomeHandler(BaseHandler):
    """Render the user's home page"""

    @web.authenticated
    @gen.coroutine
    def get(self):
        images_info = yield self._get_images_info()
        self.render('home.html', images_info=images_info)

    # private

    @gen.coroutine
    def _get_images_info(self):
        """Retrieves a dictionary containing the image and the associated
        container, if active, as values."""
        container_manager = self.application.container_manager

        apps = self.application.db.get_apps_for_user(
            self.current_user.account)

        images_info = []

        for mapping_id, app, policy in apps:
            image = yield container_manager.image(app.image)

            if image is None:
                # The user has access to an application that is no longer
                # available in docker. We just move on.
                continue

            containers = yield container_manager.containers_from_mapping_id(
                self.current_user.name,
                mapping_id)

            # We assume that we can only run one container only (although the
            # API considers a broader possibility for future extension.
            container = None
            if len(containers):
                container = containers[0]

            images_info.append({
                "image": image,
                "mapping_id": mapping_id,
                "container": container
            })
        return images_info
