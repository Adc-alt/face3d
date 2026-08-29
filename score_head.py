#!/usr/bin/env python
"""Imprimibilidad de una malla generada. Un OBJ/GLB/PLY -> los numeros que
decidieron el v7 vs v11: bordes abiertos, non-manifold, islas, volumen.

    python score_head.py malla.obj [mas.obj ...]

Sale 0 si TODAS pasan (0 abiertas / 0 non-manifold / 1 isla / volumen > 0).
"""
import sys
import numpy as np
import trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components


def carga(path):
    m = trimesh.load(path, force='mesh', process=True)
    # OBJ parte vertices en las costuras UV: sin esto cada costura cuenta
    # como borde abierto y todos los numeros salen mal.
    m.merge_vertices(merge_tex=True, merge_norm=True)
    nd = m.nondegenerate_faces()
    m.degeneradas = int((~nd).sum())
    m.update_faces(nd)
    m.remove_unreferenced_vertices()
    return m


def mide(m):
    degen = getattr(m, 'degeneradas', 0)
    f = m.faces
    e = np.sort(f[:, [0, 1, 1, 2, 2, 0]].reshape(-1, 2), axis=1)
    _, cuenta = np.unique(e, axis=0, return_counts=True)
    # islas = componentes conexas de vertices; trimesh.split() aqui llama a
    # fill_holes y arrastra networkx, ademas de mutar la malla.
    n = len(m.vertices)
    g = coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(n, n))
    n_comp, lab = connected_components(g, directed=False)
    caras = np.bincount(lab[f[:, 0]], minlength=n_comp)
    caras = caras[caras > 0]
    return {
        'verts': len(m.vertices),
        'caras': len(m.faces),
        'abiertas': int((cuenta == 1).sum()),
        'nonmanifold': int((cuenta > 2).sum()),
        'degeneradas': degen,
        'islas': int(len(caras)),
        'isla_max_%': 100.0 * caras.max() / max(caras.sum(), 1),
        'watertight': bool(m.is_watertight),
        'volumen_mm3': float(m.volume),
        'alto_mm': float(m.extents[2]),
        # un cubo teselado pasa todos los test topologicos: hay que descartarlo aparte
        'llena_bbox_%': 100.0 * float(m.volume) / max(float(np.prod(m.extents)), 1e-12),
    }


def ok(r):
    return (r['abiertas'] == 0 and r['nonmanifold'] == 0
            and r['islas'] == 1 and r['volumen_mm3'] > 0
            and r['llena_bbox_%'] < 95.0)          # >95% = es una caja, no un objeto


def main(paths):
    todo = True
    for p in paths:
        r = mide(carga(p))
        v = ok(r)
        todo &= v
        print(f"\n{'PASA' if v else 'FALLA'}  {p}")
        for k, val in r.items():
            print(f"  {k:14s} {val:>14,.2f}" if isinstance(val, float) else f"  {k:14s} {val:>14}")
    return 0 if todo else 1


def demo():
    """Autocomprobacion: un cubo pasa; el mismo cubo sin una cara, no."""
    c = trimesh.creation.box((10, 10, 10))
    r = mide(c)
    assert r['abiertas'] == 0 and r['islas'] == 1 and r['volumen_mm3'] > 0
    roto = trimesh.Trimesh(c.vertices, c.faces[:-2], process=False)
    r2 = mide(roto)
    assert not ok(r2) and r2['abiertas'] == 4, r2
    dos = c + trimesh.creation.box((4, 4, 4), trimesh.transformations.translation_matrix((50, 0, 0)))
    assert mide(dos)['islas'] == 2
    # el cubo es topologicamente impecable pero NO es un objeto valido
    assert not ok(mide(c)) and mide(c)['llena_bbox_%'] > 99
    esfera = trimesh.creation.icosphere(subdivisions=3, radius=5)
    assert ok(mide(esfera)) and mide(esfera)['llena_bbox_%'] < 95
    print("demo OK")


if __name__ == '__main__':
    a = sys.argv[1:]
    sys.exit(demo() if a == ['--demo'] else main(a) if a else print(__doc__))
