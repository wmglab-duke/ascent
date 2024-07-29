"""Defines ASCENT Exceptions.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""


class MorphologyError(Exception):
    """Exception raised when a morphology is invalid."""


class MaskError(Exception):
    """Exception raised for errors with masks.

    Only for use prior to generation of morphological classes (e.g., traces).
    """


class MethodError(Exception):
    """Exception raised when a method is used in a situation where it is not allowed."""


class JavaError(Exception):
    """Exception raised when Java encounters an error."""


class IncompatibleParametersError(LookupError):
    """Exception raised when a configuration value is valid, but conflicts with another option.

    WHEN NOT TO USE:
    If a required configuration option is missing, a KeyError should be raised instead.
    If a configuration option is invalid, a ValueError should be raised instead.
    For example, if a configuration option may only be between 0 and 1, but is set to 2, a ValueError should be raised.
    If a configuration option type is invalid, a TypeError should be raised instead.
    If a configuration option is an empty list, and should not be empty, an IndexError should be raised instead.

    Example:
    NerveMode is set to NOT_PRESENT (a valid choice) but DeformationMode is set to PHYSICS (also a valid choice).
    Each option individually is a valid choice, however, they conflict with each other.
    In this situation. a IncompatibleParametersError should be raised.
    """


class DevelopmentError(Exception):
    """Exception raised for development errors."""
