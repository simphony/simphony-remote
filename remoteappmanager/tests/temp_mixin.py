import shutil
import tempfile
import logging


class TempMixin:
    """A mixin for tests. It provides creation and cleanup of a temporary
    directory where to create files.
    """
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

        def cleanup():
            try:
                shutil.rmtree(self.tempdir)
            except OSError:
                logging.exception("Unable to delete temporary "
                                  "directory {}".format(self.tempdir))

        self.addCleanup(cleanup)

        super().setUp()
