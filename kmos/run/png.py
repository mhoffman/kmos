
from ase.io.png import PNG
from ase.data.colors import jmol_colors
from ase.data import covalent_radii
from ase.utils import rotate
from math import sqrt
import numpy as np

class MyPNG(PNG):
    def __init__(self, atoms,
                 rotation='',
                 show_unit_cell=False,
                 radii=None,
                 bbox=None,
                 colors=None,
                 model=None,
                 scale=20) :

        self.numbers = atoms.get_atomic_numbers()
        self.colors = colors
        self.model = model
        if colors is None:
            self.colors = jmol_colors[self.numbers]

        if radii is None:
            radii = covalent_radii[self.numbers]
        elif type(radii) is float:
            radii = covalent_radii[self.numbers] * radii
        else:
            radii = np.array(radii)

        natoms = len(atoms)

        if isinstance(rotation, str):
            rotation = rotate(rotation)

        A = atoms.get_cell()
        if show_unit_cell > 0:
            L, T, D = self.cell_to_lines(A)
            C = np.empty((2, 2, 2, 3))
            for c1 in range(2):
                for c2 in range(2):
                    for c3 in range(2):
                        C[c1, c2, c3] = np.dot([c1, c2, c3], A)
            C.shape = (8, 3)
            C = np.dot(C, rotation)  # Unit cell vertices
        else:
            L = np.empty((0, 3))
            T = None
            D = None
            C = None

        nlines = len(L)

        X = np.empty((natoms + nlines, 3))
        R = atoms.get_positions()
        X[:natoms] = R
        X[natoms:] = L

        r2 = radii**2
        for n in range(nlines):
            d = D[T[n]]
            if ((((R - L[n] - d)**2).sum(1) < r2) &
                (((R - L[n] + d)**2).sum(1) < r2)).any():
                T[n] = -1

        X = np.dot(X, rotation)
        R = X[:natoms]

        if bbox is None:
            X1 = (R - radii[:, None]).min(0)
            X2 = (R + radii[:, None]).max(0)
            if show_unit_cell == 2:
                X1 = np.minimum(X1, C.min(0))
                X2 = np.maximum(X2, C.max(0))
            M = (X1 + X2) / 2
            S = 1.05 * (X2 - X1)
            w = scale * S[0]
            #if w > 500:
                #w = 500
                #scale = w / S[0]
            h = scale * S[1]
            offset = np.array([scale * M[0] - w / 2, scale * M[1] - h / 2, 0])
        else:
            w = (bbox[2] - bbox[0]) * scale
            h = (bbox[3] - bbox[1]) * scale
            offset = np.array([bbox[0], bbox[1], 0]) * scale

        self.w = w
        self.h = h

        X *= scale
        X -= offset

        if nlines > 0:
            D = np.dot(D, rotation)[:, :2] * scale

        if C is not None:
            C *= scale
            C -= offset

        A = np.dot(A, rotation)
        A *= scale

        self.A = A
        self.X = X
        self.D = D
        self.T = T
        self.C = C
        self.natoms = natoms
        self.d = 2 * scale * radii

    def write(self, filename, resolution=72):
        self.filename = filename
        self.write_header(resolution=resolution)
        self.write_info()
        self.write_body()
        self.write_trailer(resolution=resolution)

    def write_info(self):
        def latex_float(f):
            float_str = "{0:.2e}".format(f)
            if "e" in float_str:
                base, exponent = float_str.split("e")
                return r"{0} \times 10^{{{1}}}".format(base, int(exponent))
            else:
                return float_str

        import matplotlib.text
        if self.model is not None:
            time = latex_float(self.model.base.get_kmc_time())

            text = matplotlib.text.Text(.05*self.w,
                                        .9*self.h,
                                        r'$t = {time}\,{{\rm s}}$'.format(**locals()),
                                        fontsize=36,
                                        bbox={'facecolor':'white', 'alpha':0.5, 'ec':'white', 'pad':1, 'lw':0 },
                                        )
            text.figure = self.figure
            text.draw(self.renderer)

    def write_header(self, resolution=72):
        from matplotlib.backends.backend_agg import RendererAgg, Figure
        from matplotlib.backend_bases import GraphicsContextBase

        try:
            from matplotlib.transforms import Value
        except ImportError:
            dpi = resolution
        else:
            dpi = Value(resolution)

        self.renderer = RendererAgg(self.w, self.h, dpi)
        self.figure = Figure()

        self.gc = GraphicsContextBase()
        self.gc.set_linewidth(.2)

    def write_trailer(self, resolution=72):
        renderer = self.renderer
        if hasattr(renderer._renderer, 'write_png'):
            # Old version of matplotlib:
            renderer._renderer.write_png(self.filename)
        else:
            from matplotlib import _png
            # buffer_rgba does not accept arguments from version 1.2.0
            # https://github.com/matplotlib/matplotlib/commit/f4fee350f9fbc639853bee76472d8089a10b40bd
            import matplotlib
            if matplotlib.__version__ < '1.2.0':
                x = renderer._renderer.buffer_rgba(0, 0)
                _png.write_png(renderer._renderer.buffer_rgba(0, 0),
                               renderer.width, renderer.height,
                               self.filename, resolution)
            else:
                x = renderer._renderer.buffer_rgba()
                _png.write_png(renderer._renderer.buffer_rgba(),
                               #renderer.width, renderer.height,
                               self.filename, resolution)

