"""Render rapido de una malla sin Blender ni OpenGL: proyeccion ortografica de los
vertices con z-buffer y sombreado N.L. Suficiente para juzgar una cara."""
import sys, numpy as np, trimesh
from PIL import Image

P = sys.argv[1]; OUT = sys.argv[2] if len(sys.argv) > 2 else 'render.png'
S, VISTAS = 420, 8

m = trimesh.load(P, force='mesh', process=True)
V = np.asarray(m.vertices, float); N = np.asarray(m.vertex_normals, float)
V -= (V.min(0) + V.max(0)) / 2
V /= np.abs(V).max()

# eje 'arriba' = el de mayor extension (una cabeza es mas alta que ancha)
up = int(np.argmax(V.max(0) - V.min(0)))
ejes = [i for i in range(3) if i != up]

tiras = []
for k in range(VISTAS):
    a = 2 * np.pi * k / VISTAS
    c, s = np.cos(a), np.sin(a)
    x = V[:, ejes[0]] * c + V[:, ejes[1]] * s          # horizontal
    y = V[:, up]                                        # vertical
    z = -V[:, ejes[0]] * s + V[:, ejes[1]] * c          # profundidad
    nz = -N[:, ejes[0]] * s + N[:, ejes[1]] * c
    ny = N[:, up]

    px = ((x * 0.95 + 1) / 2 * (S - 1)).astype(np.int32)
    py = ((1 - (y * 0.95 + 1) / 2) * (S - 1)).astype(np.int32)
    ok = (px >= 0) & (px < S) & (py >= 0) & (py < S)
    idx = py[ok] * S + px[ok]
    prof = -z[ok]                                       # menor = mas cerca

    orden = np.argsort(prof)                            # el mas cercano ultimo gana
    buf = np.full(S * S, np.nan)
    lum = np.clip(0.30 + 0.75 * (0.55 * nz[ok] + 0.45 * ny[ok]), 0, 1)
    buf[idx[orden][::-1]] = lum[orden][::-1]

    img = np.where(np.isnan(buf), 1.0, buf).reshape(S, S)
    tiras.append((img * 255).astype(np.uint8))

fila = lambda t: np.hstack(t)
hoja = np.vstack([fila(tiras[:4]), fila(tiras[4:])])
Image.fromarray(hoja).save(OUT)
print(OUT, hoja.shape, "| eje arriba =", up, "| vertices:", len(V))
