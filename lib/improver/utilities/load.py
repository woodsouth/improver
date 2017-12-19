# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# (C) British Crown Copyright 2017 Met Office.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""Module for loading cubes."""

import glob

import iris
from iris.exceptions import ConstraintMismatchError

from improver.utilities.cube_manipulation import enforce_coordinate_ordering

iris.FUTURE.netcdf_promote = True


def load_cube(filepath, constraints=None):
    """Load the filepath provided using Iris into a cube.

    Args:
        filepath (str):
            Filepath that will be loaded.
        constraints (iris.Constraint, str or None):
            Constraint to be applied when loading from the input filepath.
            This can be in the form of an iris.Constraint or could be a string
            that is intended to match the name of the cube.
            The default is None.

    Returns:
        cube (iris.cube.Cube):
            Cube that has been loaded from the input filepath given the
            constraints provided.
    """
    cube = iris.load_cube(filepath, constraint=constraints)
    # Ensure the probabilistic coordinates are the first coordinates within a
    # cube and are in the specified order.
    cube = enforce_coordinate_ordering(
        cube, ["realization", "percentile_over", "probability"])
    # Ensure the y and x dimensions are the last dimensions within the cube.
    y_name = cube.coord(axis="y").name()
    x_name = cube.coord(axis="x").name()
    cube = enforce_coordinate_ordering(cube, [y_name, x_name], anchor="end")
    return cube


def load_cubelist(filepath, constraints=None):
    """Load the filepath(s) provided using Iris into a cubelist.

    Args:
        filepath (str or list):
            Filepath(s) that will be loaded.
        constraints (iris.Constraint, str or None):
            Constraint to be applied when loading from the input filepath.
            This can be in the form of an iris.Constraint or could be a string
            that is intended to match the name of the cube.
            The default is None.

    Returns:
        cubelist (iris.cube.CubeList):
            CubeList that has been created from the input filepath given the
            constraints provided.
    """
    # If the filepath is a string, then use glob, in case the str contains
    # wildcards.
    if isinstance(filepath, str):
        filepaths = glob.glob(filepath)
    else:
        filepaths = filepath

    # Constuct a cubelist using the load_cube function.
    cubelist = iris.cube.CubeList([])
    for filepath in filepaths:
        try:
            cube = load_cube(filepath, constraints=constraints)
        except ConstraintMismatchError:
            continue
        cubelist.append(cube)
    return cubelist
