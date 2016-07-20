"""Additional traitlets that we use in our application."""
from traitlets import Unicode


class UnicodeOrFalse(Unicode):
    info_text = 'a unicode string or False'

    def validate(self, obj, value):
        if value is False:
            return value
        return super().validate(obj, value)


def set_traits_from_dict(traited_instance, d):
    """Given a class with traitlets and a dictionary with keys corresponding
    to the traitlet names, set the traitlets to the associated dict values.

    Note: if a set operation fails, the appropriate traitlet exception is
    raised. Traitlets that were already set won't be rolled back.
    """
    dict_keys = d.keys()
    traitlet_names = traited_instance.trait_names()
    for name in [x for x in traitlet_names if x in dict_keys]:
        traited_instance.set_trait(name, d[name])


def as_dict(traited_instance):
    """Returns a dictionary from the traited class, with keys
    equal to trait names and values the corresponding values."""
    return {attr: getattr(traited_instance, attr)
            for attr in traited_instance.trait_names()}
