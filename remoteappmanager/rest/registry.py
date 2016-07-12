class Registry:
    def __init__(self):
        self._registered_types = {}

    def register(self, typ):
        """Registers a Resource type with an appropriate
        collection name. A collection name is a pluralized
        version of the resource, created by lowercasing
        the class name and adding an "s".
        The resulting collection name will be used in the URL
        representing the resource. For example, a resource Image
        will have URLs of the type

        http://example.com/api/v1/images/identifier/

        The collection name can always be overridden by specifying
        __collection_name__ in the resource class.
        """
        if hasattr(typ, "__collection_name__"):
            collection_name = typ.__collection_name__
        else:
            collection_name = typ.__name__.lower() + "s"

        self._registered_types[collection_name] = typ

    def __getitem__(self, collection_name):
        """Returns the class from the collection name with the
        indexing operator"""
        return self._registered_types[collection_name]


#: global registry for registration of the classes.
registry = Registry()
