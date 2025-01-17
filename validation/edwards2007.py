import matplotlib.pyplot as plt
import numpy as np
import gmsh
from pygmsh import *
import time

import traceon.geometry as G
import traceon.excitation as E
import traceon.plotting as P
import traceon.solver as S

import util


def create_geometry(MSF, symmetry):
    """Create the geometry g5 (figure 2) from the following paper:
    D. Edwards. High precision electrostatic potential calculations for cylindrically
    symmetric lenses. 2007.
    """
    with G.Geometry(symmetry) as geom:
        points = [
            [0, 0],
            [0, 5],
            [12, 5],
            [12, 15],
            [0, 15],
            [0, 20],
            [20, 20],
            [20, 0]
        ]

        _3d = symmetry != G.Symmetry.RADIAL
        
        geom.set_mesh_size_factor(MSF)
        
        if _3d:
            points = [geom.add_point([p[0], 0.0, p[1]]) for p in points]
        else:
            points = [geom.add_point(p) for p in points]
        
        l1 = geom.add_line(points[1], points[2])
        l2 = geom.add_line(points[2], points[3])
        l3 = geom.add_line(points[3], points[4])
        
        l4 = geom.add_line(points[0], points[-1])
        l5 = geom.add_line(points[-3], points[-2])
        l6 = geom.add_line(points[-2], points[-1])
        
        if _3d:
            inner = G.revolve_around_optical_axis(geom, [l1, l2, l3])
            boundary = G.revolve_around_optical_axis(geom, [l4, l5, l6])
            
            geom.add_physical(inner, 'inner')
            geom.add_physical(boundary, 'boundary')
            
            return geom.generate_mesh()
        else:
            geom.add_physical([l1, l2, l3], 'inner')
            geom.add_physical([l4, l5, l6], 'boundary')
            
            return geom.generate_mesh()

def compute_field(geometry):
    excitation = E.Excitation(geometry)
    excitation.add_voltage(boundary=0, inner=10)

    use_fmm = geometry.symmetry == G.Symmetry.THREE_D
    field = S.solve_bem(excitation, use_fmm=use_fmm)
    
    return excitation, field

def compute_error(excitation, field, geometry):
    st = time.time()

    _3d = excitation.mesh.symmetry != G.Symmetry.RADIAL
    
    if _3d:
        pot = field.potential_at_point(np.array([12, 0.0, 4]))
    else:
        pot = field.potential_at_point(np.array([12, 4]))
    print(f'Time for computing potential {(time.time()-st)*1000:.2f} ms')
    
    correct = 6.69099430708
    print('Potential: ', pot)
    print('Correct: ', correct)
    return excitation, abs(pot/correct - 1)

util.parser.description = '''Compute the potential at point (12, 4) inside two coaxial cylinders. See paper:

High precision electrostatic potential calculations for cylindrically symmetric lenses. David Edwards. 2007.
'''

util.parse_validation_args(create_geometry, compute_field, compute_error, boundary='blue', inner='orange')

