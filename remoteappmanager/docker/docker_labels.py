"""Contains established common dictionary of labels
that we use to add information to docker images or containers."""

# Namespaces for our labels. Must end with a dot.
SIMPHONY_NS = "eu.simphony-project.docker."

# User interface name for the image
UI_NAME = SIMPHONY_NS+"ui_name"

# A 128x128px icon to represent the image
ICON_128 = SIMPHONY_NS+"icon_128"

# A long description of the image
DESCRIPTION = SIMPHONY_NS+"description"
