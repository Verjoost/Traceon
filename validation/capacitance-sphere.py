import time
import argparse

import numpy as np
from pygmsh import *
import matplotlib.pyplot as plt

import traceon.geometry as G
import traceon.excitation as E
import traceon.solver as S
import traceon.plotting as P

import util

r1 = 0.5
r2 = 1.0

r3 = 0.6
r4 = 0.9

def create_geometry(MSF, symmetry):
     
    with G.Geometry(symmetry) as geom:
        center = geom.add_point([0.0, 0.0])
        
        def add_shell(r, reorient=False, factor=1.0):
            
            if symmetry == G.Symmetry.RADIAL:
                points = [[0,-r], [r, 0], [0,r]]
            else:
                points = [[0,0,-r], [r,0, 0], [0,0,r]]
            
            p = [geom.add_point(p) for p in points]

            if not reorient:
                arcs = [geom.add_circle_arc(p[0], center, p[1]), geom.add_circle_arc(p[1], center, p[2])]
            else:
                arcs = [geom.add_circle_arc(p[2], center, p[1]), geom.add_circle_arc(p[1], center, p[0])]

            if symmetry == G.Symmetry.RADIAL:
                return arcs
            else:
                return G.revolve_around_optical_axis(geom, arcs, factor=factor)
         
        l1 = add_shell(r1)
        d1 = add_shell(r3, reorient=symmetry == G.Symmetry.RADIAL)
        d2 = add_shell(r4, reorient=symmetry != G.Symmetry.RADIAL)
        l2 = add_shell(r2, reorient=True)
        
        geom.add_physical(l1, 'inner')
        geom.add_physical(l2, 'outer')
        geom.add_physical([*d1, *d2], 'dielectric')
        
        geom.set_mesh_size_factor(MSF)
         
        return geom.generate_mesh()

K=2

def compute_field(geom):
    exc = E.Excitation(geom)
    exc.add_voltage(inner=1)
    exc.add_voltage(outer=0)
    exc.add_dielectric(dielectric=K)
     
    use_fmm = geom.symmetry == G.Symmetry.THREE_D
    field = S.solve_bem(exc, use_fmm=use_fmm)
    
    return exc, field

def compute_error(exc, field, geom):
    x = np.linspace(0.55, 0.95)
    f = [field.field_at_point(np.array([x_, 0.0, 0.0]))[0] for x_ in x]
     
    vertices = field.vertices
    charges = field.charges
     
    # Find the charges
    _, names = exc.get_active_elements()
    Q = {n:field.charge_on_elements(i) for n, i in names.items()}
    print(Q)
    
    expected = 4/( (1/r1 - 1/r3) + (1/r3 - 1/r4)/K + (1/r4 - 1/r2))
    capacitance = (abs(Q['outer']) + abs(Q['inner']))/2
    print('Capacitance found: \t%.10f' % capacitance)
    print('Capacitance expected: \t%.10f' % expected)
    error = abs(capacitance/expected - 1)
    return exc, error

util.parser.description = '''Compute the capacitance of two concentric spheres with a layer of dielectric material in between.'''
util.parse_validation_args(create_geometry, compute_field, compute_error, inner='blue', outer='darkblue', dielectric='green')

