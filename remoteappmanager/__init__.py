MAJOR = 0
MINOR = 10
MICRO = 0
IS_RELEASED = False

__version__ = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

if not IS_RELEASED:
    __version__ += '.dev0'
