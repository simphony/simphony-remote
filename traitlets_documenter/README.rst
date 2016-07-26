Traitlets Documenter
--------------------

A sphinx autodoc extension for documenting Traitlets classes.
Currently support documenting classes with members of Traitlets TraitType.
This code is inspired from `Traits Documenter <https://github.com/enthought/trait-documenter>`_

Installation
^^^^^^^^^^^^
This package is installed as a subpackage of `simphony/simphony-remote <https://github.com/simphony/simphony-remote>`_.


Usage
^^^^^
Add `traitlets_documenter` to the extensions variables in your `conf.py`::

  extensions.append('traitlets_documenter')
