from sphinx.ext.autodoc import ClassLevelDocumenter
from traitlets import TraitType

from .util import get_trait_definition, DefinitionError


class ClassTraitletDocumenter(ClassLevelDocumenter):

    objtype = 'traitletattribute'
    directivetype = 'attribute'
    member_order = 60

    # must be higher than other attribute documenters
    priority = 12

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        """ Check that the documented member is a trait instance.
        """
        return isinstance(member, TraitType)

    def document_members(self, all_members=False):
        pass

    def add_content(self, more_content, no_docstring=False):
        """ Add content

        If the help attribute is defined, add the help content,
        otherwise, add the info content.

        If the default value is found in the definition,
        add the default value as well
        """
        # Never try to get a docstring from the trait object.
        super(ClassTraitletDocumenter, self).add_content(
            more_content, no_docstring=True)

        if hasattr(self, 'get_sourcename'):
            sourcename = self.get_sourcename()
        else:
            sourcename = u'<autodoc>'

        # Get help message, if defined, otherwise, add the info
        if self.object.help:
            self.add_line(self.object.help, sourcename)
        else:
            self.add_line(self.object.info(), sourcename)

        # Add default value if it is coded in the definition,
        # otherwise it maybe dynamically calculated and we don't want to
        # include it.
        try:
            definition = get_trait_definition(self.parent, self.object_name)
        except DefinitionError as error:
            self.directive.warn(error.args[0])
        else:
            default_value = self.object.default_value_repr()
            if default_value in definition:
                self.add_line('', sourcename)
                self.add_line(
                    'Default: {}'.format(default_value),
                    sourcename)

    def add_directive_header(self, sig):
        """ Add the sphinx directives.

        Add the 'attribute' directive with the annotation option
        set to the traitlet type

        """
        ClassLevelDocumenter.add_directive_header(self, sig)
        if hasattr(self, 'get_sourcename'):
            sourcename = self.get_sourcename()
        else:
            sourcename = u'<autodoc>'

        trait_type = type(self.object).__name__
        self.add_line(
            '   :annotation: = {0}'.format(trait_type), sourcename)
