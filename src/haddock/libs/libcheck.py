"""Routines to check quality of values."""
from functools import partial
from operator import gt


def compare(
        m,
        n,
        pref,
        compare,
        exception, message=):
    """
    Compare `m` to `n` values according to specific rules.

    Parameters
    ----------
    m, n : anything
        The values to compare.

    pref : callable
        A function to apply to `m` and `n` before comparison.

    compare : callable
        The function that compares `m` and `n`. The return value will
        be evaluated to boolean.

    exception : Python Exception
        The Exception that raises if `compare` returns False.

    message : str
        The exception message.

    Returns
    -------
    The value of `m` after applying `pref` if result of `compare` is
    True.
    """
    treated_m = pref(m)
    treated_n = pref(n)

    if compare(treated_m, treated_n):
        return treated_m
    else:
        raise exception(message)


is_positive_int = partial(m=0, pref=int, compare=gt, exception=ValueError)
