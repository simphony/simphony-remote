import os

from tornado import web, gen
from tornado.httpclient import HTTPError
from traitlets import default, Unicode

from remoteappmanager.handlers.base_handler import BaseHandler


class UploadHandler(BaseHandler):
    """ Upload files to the user's home directory
    """

    upload_target = Unicode()

    @default('upload_target')
    def _upload_target_default(self):
        """ The directory where the file should be uploaded to
        """
        return os.environ.get('HOME')

    @gen.coroutine
    def get(self):
        self.render('upload.html')

    @web.authenticated
    @gen.coroutine
    def post(self):
        if not self.upload_target:
            raise HTTPError(500,
                            "Target directory cannot be found. "
                            "Please notify system admin.")

        for file_info in self.request.files['upload_files']:
            target_path = os.path.join(self.upload_target,
                                       os.path.basename(file_info.filename))

            with open(target_path, 'wb') as fh:
                fh.write(file_info.body)

        self.finish('Uploaded {0} files to {1}'.format(
            len(self.request.files['upload_files']), self.upload_target))
