"""Gear to control the number of cores used in HADDOCK3."""
import os

from libfuncpy import vartial

from haddock.libs.libcli import add_general_argument


_help = \
"""Number of CPU cores to use during calculations. Defaults to the available
number minus one."""


def get_default_ncores():
    """
    Get the default number of cores to be used by HADDOCK3.

    By default, the number of cores specified is the maximum minus 1.
    """
    return os.cpu_count() - 1


set_ncores = vartial(
    is_positive_int,
    message="The number of CPU cores selected must be positive.",
    )


add_ncores_arg = vartial(
    '-n',
    '--ncores',
    default=os.cpu_count() - 1,
    help=_help,
    type=int,
    )
"""Add `ncores` parameter to a `argparse.ArgumentParser` object."""
