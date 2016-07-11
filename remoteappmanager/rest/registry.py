class Registry:
    def __init__(self):
        self._registered_types = {}

    def register(self, typ):
        collection_name = typ.__name__.lower() + "s"
        self._registered_types[collection_name] = typ

    def __getitem__(self, name):
        return self._registered_types[name]


registry = Registry()
