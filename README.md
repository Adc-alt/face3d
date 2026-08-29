# face3d — cara 3D a partir de una foto

Tubería para convertir **una foto** en una **cabeza 3D imprimible** (figurina personalizada).
El cuerpo es una fase posterior.

Ficha de la figura ya enviada a JLC: **[FICHA_FIGURA_ENVIADA.md](FICHA_FIGURA_ENVIADA.md)**

Lee primero: **[INVESTIGACION_MODELOS_CARA.md](INVESTIGACION_MODELOS_CARA.md)** — qué modelo
elegimos, por qué, y cuál es el criterio de aceptación.

## Herramientas

| Script | Qué hace |
|---|---|
| `crop.py` | Recorta cabeza y busto de la foto original a partir de puntos de referencia leídos sobre una rejilla |
| `quitafondo.py` | Quita el fondo (rembg/u2net) y deja un PNG RGBA |
| `score_head.py` | **Puntúa imprimibilidad**: aristas abiertas, non-manifold, islas, volumen, llena_bbox |
| `ref_cara.py` | **Mide nivel de detalle** de la banda de la cara (`z > 136`): densidad y arista mediana |
| `render.py` | Render ortográfico sin Blender ni OpenGL, para mirar una malla rápido |

Los dos medidores traen autocomprobación:

```bash
./venv/bin/python score_head.py --demo
./venv/bin/python ref_cara.py --demo
```

## Reglas duras del proyecto

- **La cara nunca se reconstruye, remalla ni voxeliza.** Operativamente: ningún vértice con `z > 136.0` se mueve.
- **Los colores no se retocan.**
- **Las gafas se quedan.**

## Estado

Referencia a batir medida sobre el v7 de Tripo: 430.209 caras, 10.573 caras/cm²,
arista mediana 0,142 mm, cabeza de 34 mm.
**Generaciones propias válidas: ninguna todavía.**

`hy_license.txt` se guarda como prueba: la licencia de Hunyuan3D excluye la UE, *incluidos
sus outputs*. Por eso está descartado.
