"""Mide el 'nivel de detalle' de la cara de referencia (v7 de Tripo).

La banda z > Z_CARA es la que el usuario prohibe tocar: es la cara real.
Sacamos de ahi la especificacion que cualquier modelo nuevo tiene que igualar.
"""
import sys
import numpy as np
import trimesh

Z_CARA = 136.0


def banda(m, z=Z_CARA):
    # una cara entra solo si sus 3 vertices estan por encima: asi no arrastramos
    # el triangulo de transicion cuello/barbilla ni falseamos el area
    dentro = (m.vertices[m.faces][:, :, 2] > z).all(axis=1)
    sub = m.submesh([np.where(dentro)[0]], append=True)
    return sub


def mide(m, nombre):
    v, f = m.vertices, m.faces
    e = np.sort(f[:, [0, 1, 1, 2, 2, 0]].reshape(-1, 2), axis=1)
    e = np.unique(e, axis=0)
    lon = np.linalg.norm(v[e[:, 0]] - v[e[:, 1]], axis=1)
    area = float(m.area)                      # mm^2
    ext = m.extents
    return {
        'nombre': nombre,
        'verts': len(v),
        'caras': len(f),
        'area_mm2': round(area, 1),
        'caras_por_cm2': round(len(f) / (area / 100.0), 1),
        'arista_mediana_mm': round(float(np.median(lon)), 4),
        'arista_p95_mm': round(float(np.percentile(lon, 95)), 4),
        'ancho_mm': round(float(ext[0]), 2),
        'fondo_mm': round(float(ext[1]), 2),
        'alto_mm': round(float(ext[2]), 2),
    }


def demo():
    # una esfera de radio conocido: comprobamos que area y densidad cuadran
    s = trimesh.creation.icosphere(subdivisions=3, radius=10.0)
    r = mide(s, 'esfera_r10')
    assert abs(r['area_mm2'] - 4 * np.pi * 100) / (4 * np.pi * 100) < 0.02, r
    assert abs(r['caras'] / (r['area_mm2'] / 100.0) - r['caras_por_cm2']) < 0.1
    # y que la banda superior de la esfera se queda con ~la mitad de la altura
    b = banda(s, 0.0)
    assert 0 < len(b.faces) < len(s.faces), len(b.faces)
    print('demo OK')


if __name__ == '__main__':
    if '--demo' in sys.argv:
        demo()
        sys.exit(0)
    for p in sys.argv[1:]:
        m = trimesh.load(p, force='mesh', process=True)
        m.merge_vertices(merge_tex=True, merge_norm=True)
        print(f'--- {p}')
        print('   completo:', mide(m, 'completo'))
        print('   cara z>%.0f:' % Z_CARA, mide(banda(m), 'cara'))
