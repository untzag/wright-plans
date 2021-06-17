__all__ = [
        "make_one_nd_step",
        "scan",
        "rel_scan",
        "list_scan",
        "rel_list_scan",
        "list_grid_scan",
        "rel_list_grid_scan",
        "grid_scan",
        "rel_grid_scan",
        "scan_nd",
        ]

from graphlib import TopologicalSorter
from typing import Dict, List, Optional

import bluesky.plan_stubs
from bluesky import plans as bsp
import toolz

from bluesky.protocols import Readable, Movable

from ._constants import Constant
from ._units import ureg, get_units

import pydantic

def make_one_nd_step(constants=None, axis_units=None, per_step=None):
    """Generate a one_nd_step function for given metadata.

    The fields taken into account are:
    `axis_units`: a map of motor names to string of pint compatible units
    `constants`: a map of motor names to tuple of (string units, list of (coeff: float, var: string))
    `motors` is a mapping of motor names to motor objects
    """
    if per_step is None:
        per_step = bluesky.plan_stubs.one_nd_step
    if not constants and not axis_units:
        # Nothing special to do, just return original method
        return per_step
    if not constants:
        constants = {}
    if not axis_units:
        axis_units = {}

    sorter = TopologicalSorter({})
    for var, const in constants.items():
        sorter.add(var, *[x.var for x in const.terms])

    order = [*sorter.static_order()]

    def one_nd_step(detectors, step, pos_cache):
        """Version of bluesky.plan_stubs.one_nd_step with support for constants and units."""
        # Translate axes from scan units to native units
        for mot, units in axis_units.items():
            mot_units = get_units(mot, units)
            quantity = ureg.Quantity(step[mot], units)
            if mot_units:
                quantity = quantity.to(mot_units)
            step[mot] = quantity.magnitude

        # fill out constants in topological order, ignore "", do math in constant's units
        for mot in order:
            if mot not in constants:
                continue
            const = constants[mot]
            const_mot_units = get_units(mot, const.units)
            step[mot] = const.evaluate(step, const_mot_units)
            
        yield from per_step(detectors, step, pos_cache)

    return one_nd_step

def _axis_units_from_args(args, n):
    return {m:u for m,*_,u in toolz.partition(n, args) if u}

def scan(detectors, *args, num=None, constants=None, per_step=None, md=None):
    nargs = 4
    axis_units = _axis_units_from_args(args, nargs)
    per_step = make_one_nd_step(constants, axis_units, per_step)
    args = [x for i,x in enumerate(args) if not i%nargs == nargs-1]
    yield from bsp.scan(detectors, *args, num=num, per_step=per_step, md=md)

def rel_scan(detectors, *args, num=None, constants=None, per_step=None, md=None):
    nargs = 4
    axis_units = _axis_units_from_args(args, nargs)
    per_step = make_one_nd_step(constants, axis_units, per_step)
    args = [x for i,x in enumerate(args) if not i%nargs == nargs-1]
    yield from bsp.rel_scan(detectors, *args, num=num, per_step=per_step, md=md)

def list_scan(detectors, *args, constants=None, per_step=None, md=None):
    nargs=3
    axis_units = _axis_units_from_args(args, nargs)
    per_step = make_one_nd_step(constants, axis_units, per_step)
    args = [x for i,x in enumerate(args) if not i%nargs == nargs-1]
    yield from bsp.list_scan(detectors, *args, per_step=per_step, md=md)

def rel_list_scan(detectors, *args, constants=None, per_step=None, md=None):
    nargs=3
    axis_units = _axis_units_from_args(args, nargs)
    per_step = make_one_nd_step(constants, axis_units, per_step)
    args = [x for i,x in enumerate(args) if not i%nargs == nargs-1]
    yield from bsp.rel_list_scan(detectors, *args, per_step=per_step, md=md)

def list_grid_scan(detectors, *args, constants=None, snake_axes=False, per_step=None, md=None):
    nargs=3
    axis_units = _axis_units_from_args(args, nargs)
    per_step = make_one_nd_step(constants, axis_units, per_step)
    args = [x for i,x in enumerate(args) if not i%nargs == nargs-1]
    yield from bsp.list_grid_scan(detectors, *args, snake_axes=snake_axes, per_step=per_step, md=md)

def rel_list_grid_scan(detectors, *args, constants=None, snake_axes=False, per_step=None, md=None):
    nargs=3
    axis_units = _axis_units_from_args(args, nargs)
    per_step = make_one_nd_step(constants, axis_units, per_step)
    args = [x for i,x in enumerate(args) if not i%nargs == nargs-1]
    yield from bsp.rel_list_grid_scan(detectors, *args, snake_axes=snake_axes, per_step=per_step, md=md)

def grid_scan(detectors: List[pydantic.PyObject], *args, constants: Optional[Dict[pydantic.PyObject, pydantic.PyObject]]=None, snake_axes: bool=False, per_step=None, md=None):
    nargs=5
    axis_units = _axis_units_from_args(args, nargs)
    per_step = make_one_nd_step(constants, axis_units, per_step)
    args = [x for i,x in enumerate(args) if not i%nargs == nargs-1]
    yield from bsp.grid_scan(detectors, *args, snake_axes=snake_axes, per_step=per_step, md=md)

def rel_grid_scan(detectors, *args, constants=None, snake_axes=False, per_step=None, md=None):
    nargs=5
    axis_units = _axis_units_from_args(args, nargs)
    per_step = make_one_nd_step(constants, axis_units, per_step)
    args = [x for i,x in enumerate(args) if not i%nargs == nargs-1]
    yield from bsp.rel_grid_scan(detectors, *args, snake_axes=snake_axes, per_step=per_step, md=md)

def scan_nd(detectors, cycler, *, axis_units=None, constants=None, per_step=None, md=None):
    per_step = make_one_nd_step(constants, axis_units, per_step)
    yield from bsp.scan_nd(detectors, cycler, per_step=per_step, md=md)



