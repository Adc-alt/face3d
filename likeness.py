"""Medidor de parecido: coseno ArcFace entre una foto y una malla 3D.

Como no sabemos a priori hacia donde 'mira' la cara de una malla generada,
la giramos en yaw y nos quedamos con la vista donde el propio detector de
caras (el mismo InsightFace) encuentra una cara con mas confianza. Esa vista
es la que se compara contra la foto.

Uso:
    python3 likeness.py foto.jpg malla.obj [malla2.obj ...]

Requiere pesos de InsightFace (buffalo_l) — se descargan solos la primera vez
(necesita internet). Licencia no comercial: valido para medir en desarrollo,
NO para el pipeline de venta (ver Fase 4.2 en Little Me / INVESTIGACION).
"""
import sys
import numpy as np
import cv2
import trimesh
from insightface.app import FaceAnalysis

S = 512          # resolucion de cada vista renderizada
VISTAS = 16       # pasos de yaw (360 / 16 = 22.5 grados)


def cargar_color(m):
    """Vuelca la textura UV a color por vertice (mismo truco que usa DECA/EMOCA
    para poder comparar render contra foto con un detector de caras normal)."""
    vis = m.visual
    if hasattr(vis, 'to_color'):
        vis = vis.to_color()
    col = np.asarray(vis.vertex_colors)[:, :3].astype(np.float64) / 255.0
    return col


def render_vistas(path):
    m = trimesh.load(path, force='mesh', process=True)
    m.merge_vertices(merge_tex=True, merge_norm=True)
    V = np.asarray(m.vertices, float)
    N = np.asarray(m.vertex_normals, float)
    C = cargar_color(m)
    V = V - (V.min(0) + V.max(0)) / 2
    V = V / np.abs(V).max()

    up = int(np.argmax(V.max(0) - V.min(0)))
    ejes = [i for i in range(3) if i != up]

    vistas = []
    for k in range(VISTAS):
        a = 2 * np.pi * k / VISTAS
        c, s = np.cos(a), np.sin(a)
        x = V[:, ejes[0]] * c + V[:, ejes[1]] * s
        y = V[:, up]
        z = -V[:, ejes[0]] * s + V[:, ejes[1]] * c
        nz = -N[:, ejes[0]] * s + N[:, ejes[1]] * c
        ny = N[:, up]

        px = ((x * 0.95 + 1) / 2 * (S - 1)).astype(np.int32)
        py = ((1 - (y * 0.95 + 1) / 2) * (S - 1)).astype(np.int32)
        ok = (px >= 0) & (px < S) & (py >= 0) & (py < S)
        idx = py[ok] * S + px[ok]
        prof = -z[ok]

        orden = np.argsort(prof)
        buf = np.full((S * S, 3), 1.0)
        lum = np.clip(0.35 + 0.70 * (0.55 * nz[ok] + 0.45 * ny[ok]), 0, 1)[:, None]
        rgb = (C[ok] * lum)
        buf[idx[orden][::-1]] = rgb[orden][::-1]

        img = (buf.reshape(S, S, 3) * 255).astype(np.uint8)
        vistas.append(cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    return vistas


def mejor_cara(app, imgs):
    """De una lista de imagenes BGR, la que tenga la cara mas confiada y grande."""
    mejor = None
    for img in imgs:
        caras = app.get(img)
        for c in caras:
            area = (c.bbox[2] - c.bbox[0]) * (c.bbox[3] - c.bbox[1])
            score = c.det_score * area
            if mejor is None or score > mejor[0]:
                mejor = (score, c.normed_embedding, img)
    return mejor


def coseno(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def parecido(app, foto_path, malla_path):
    foto = cv2.imread(foto_path)
    caras_foto = app.get(foto)
    if not caras_foto:
        raise SystemExit(f'no se detecta cara en {foto_path}')
    emb_foto = max(caras_foto, key=lambda c: c.det_score).normed_embedding

    vistas = render_vistas(malla_path)
    r = mejor_cara(app, vistas)
    if r is None:
        return None  # ninguna vista de la malla tiene una cara detectable
    _, emb_malla, _ = r
    return coseno(emb_foto, emb_malla)


def demo():
    # una esfera no tiene cara: debe devolver None, no reventar
    s = trimesh.creation.icosphere(subdivisions=3, radius=10.0)
    s.visual = trimesh.visual.ColorVisuals(s, vertex_colors=[200, 180, 160, 255])
    s.export('/tmp/_esfera_demo.obj')
    app = FaceAnalysis(name='buffalo_l')
    app.prepare(ctx_id=-1, det_size=(320, 320))
    vistas = render_vistas('/tmp/_esfera_demo.obj')
    assert mejor_cara(app, vistas) is None
    print('demo OK (esfera sin cara -> None)')


if __name__ == '__main__':
    if '--demo' in sys.argv:
        demo(); sys.exit(0)
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)

    app = FaceAnalysis(name='buffalo_l')
    app.prepare(ctx_id=-1, det_size=(320, 320))

    foto = sys.argv[1]
    for malla in sys.argv[2:]:
        score = parecido(app, foto, malla)
        if score is None:
            print(f'{malla}: sin cara detectable en ninguna vista')
        else:
            print(f'{malla}: parecido = {score:.3f}')
