"""
Control and help the command-line client interface (CLI).

Contaings functions and logic dedicated to control and help building the
command-line interface and that are useful for the whole HADDOCK3
project.
"""
import argparse


def add_general_argument(parser, *args, **kwargs):
    """
    Add a command to parser.

    `*args` and `**kwargs` will populate the `.add_argument()` method.

    Parameters
    ----------
    parser : `argparse.ArgumentParser` object.

    Returns
    -------
    None
        Modifies `parser` in place.
    """
    parser.add_argument(*args, **kwargs)
