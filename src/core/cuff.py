from matplotlib import pyplot
from shapely.geometry import Point
from descartes import PolygonPatch

fig = pyplot.figure(1)

# LivaNova
r_cuff_in = 1  # um
cuff_boundary = Point(0, 0).buffer(r_cuff_in)

ax = fig.add_subplot(111)
patch1 = PolygonPatch(cuff_boundary)
ax.add_patch(patch1)
pyplot.show()