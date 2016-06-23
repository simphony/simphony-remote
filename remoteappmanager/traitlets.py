"""Additional traitlets that we use in our application."""
from traitlets import Unicode


class UnicodeOrFalse(Unicode):
    info_text = 'a unicode string or False'

    def validate(self, obj, value):
        if value is False:
            return value
        return super().validate(obj, value)
