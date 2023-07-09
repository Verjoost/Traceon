import numpy as np

from traceon import focus as F
from traceon import tracing as T

v1 = T.velocity_vec(10, [-1e-3, -1])
v2 = T.velocity_vec(10, [1e-3, -1])

p1 = np.concatenate( (3*v1, v1) )[np.newaxis, :]
p2 = np.concatenate( (3*v2, v2) )[np.newaxis, :]

(x, z) = F.focus_position([p1, p2])

assert np.isclose(x, 0) and np.isclose(z, 0)

p1[0, 0] += 1
p2[0, 0] += 1

(x, z) = F.focus_position([p1, p2])
assert np.isclose(x, 1) and np.isclose(z, 0)

p1[0, 1] += 1
p2[0, 1] += 1

(x, z) = F.focus_position([p1, p2])
assert np.isclose(x, 1) and np.isclose(z, 1)


v1 = T.velocity_vec_spherical(1, 0, 0)
v2 = T.velocity_vec_spherical(5, 1/30, 1/30)
v3 = T.velocity_vec_spherical(10, 1/30, np.pi/2)

p1 = np.concatenate( (v1, v1) )[np.newaxis, :]
p2 = np.concatenate( (v2, v2) )[np.newaxis, :]
p3 = np.concatenate( (v3, v3) )[np.newaxis, :]

print(F.focus_position([p1, p2, p3]))















