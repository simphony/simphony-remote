__all__ = ['setup']


def setup(app):
    """ Add the TraitletDocumenter in the current sphinx autodoc instance.

    """
    from traitlets_documenter.class_traitlets_documenter import (
        ClassTraitletDocumenter)

    app.add_autodocumenter(ClassTraitletDocumenter)
