import ast
import inspect
import collections
from _ast import ClassDef, Assign, Name

import astor


class DefinitionError(Exception):
    pass


def get_trait_definition(parent, trait_name):
    """ Retrieve the Trait attribute definition from the source file.

    Parameters
    ----------
    parent :
        The module or class where the trait is defined.

    trait_name : string
        The name of the trait.

    Returns
    -------
    definition : string
        The trait definition from the source.

    """
    # Get the class source.
    source = inspect.getsource(parent)
    nodes = ast.parse(source)

    if not inspect.ismodule(parent):
        for node in ast.iter_child_nodes(nodes):
            if isinstance(node, ClassDef):
                parent_node = node
                break
        else:
            message = 'Could not find class definition {0} for {1}'
            raise DefinitionError(message.format(parent, trait_name))
    else:
        parent_node = nodes

    # Get the container node(s)
    targets = collections.defaultdict(list)
    for node in ast.walk(parent_node):
        if isinstance(node, Assign):
            target = trait_node(node, trait_name)
            if target is not None:
                targets[node.col_offset].append((node, target))

    if len(targets) == 0:
        message = 'Could not find trait definition of {0} in {1}'
        raise DefinitionError(message.format(trait_name, parent))
    else:
        # keep the assignment with the smallest column offset
        assignments = targets[min(targets)]
        # we always get the last assignment in the file
        node, name = assignments[-1]

    return astor.to_source(node.value).strip()


def trait_node(node, trait_name):
    target = node.targets[0]
    if isinstance(target, Name) and target.id == trait_name:
        return node
