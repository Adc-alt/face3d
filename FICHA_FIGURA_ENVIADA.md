# Ficha técnica — figurina enviada a JLC3DP (v11)

Fichero medido: `figurina_fullcolor_v11_ligero.obj`
(el que va dentro de `figurina_v11_jpg.zip`, el paquete que se sube al portal;
vértices, UV y caras byte a byte iguales al `figurina_fullcolor_v11.obj`, solo
sin las líneas `vn`).

| | |
|---|---|
| **Pedido** | W2026080406151959 |
| **Contacto** | Elinor — elinor@jlcpcb.com |
| **Proceso** | WJP resina, color completo + oil spraying |
| **Fecha del paquete** | 2026-08-03 |
| **Unidades del fichero** | milímetros, 1 unidad = 1 mm |
| **Origen** | Z=0 en la base, centrada en XY (centro 0,0) |

---

## Dimensiones generales

| Medida | Valor |
|---|---|
| **Alto total** | **170,00 mm** |
| **Ancho máximo (X)** | **74,45 mm** — a z = 80–90 mm (envergadura de los brazos) |
| **Fondo máximo (Y)** | **36,61 mm** |
| **Huella de apoyo** | 58,93 × 28,12 mm |
| Caja envolvente | 74,45 × 36,61 × 170,00 mm |
| **Volumen** | **122,361 cm³** (122.361 mm³) |
| Área de superficie | 269,3 cm² |
| Masa estimada en resina | **141–147 g** (a 1,15–1,20 g/cm³) |
| Ocupación de la caja | 26,4 % |

## Perfil de anchura por altura

| Altura z (mm) | Ancho X (mm) | Fondo Y (mm) | Qué es |
|---|---|---|---|
| 0–10 | 59,71 | 32,45 | base / pies |
| 10–50 | 49,60 → 46,23 | ~20–21 | piernas |
| 50–60 | 69,35 | 22,38 | manos / caderas |
| 60–70 | 73,64 | 29,54 | brazos |
| **80–90** | **74,45** | 31,24 | **punto más ancho** |
| 100–120 | 68,98 → 67,46 | ~30 | pecho |
| 120–130 | 59,25 | 25,34 | hombros |
| 130–140 | 27,51 | 26,25 | cuello |
| 140–170 | 25,50 → 28,60 | 30,5–31,3 | cabeza |

## La cabeza

Banda `z > 136 mm` — **la zona protegida: ningún vértice de aquí se ha movido nunca.**

| Medida | Valor |
|---|---|
| **Dimensiones** | **28,84 × 32,57 × 34,00 mm** |
| Arranca en | z = 136 mm (80 % de la altura total) |
| Vértices / caras | 215.130 / 430.209 |
| Área | 40,7 cm² |
| **Densidad de malla** | **10.573 caras/cm²** |
| **Arista mediana** | **0,142 mm** ← el detalle más fino que resolvió Tripo |
| Arista p95 | 0,394 mm |
| Interior | macizo — aire sellado dentro: 0,03 mm³ |

**El 66 % de todos los triángulos de la figura están en la cabeza**, que es solo el
15 % del área. Es 4,4× más densa que el resto.

Verificado: la cara es idéntica a la del v7 original de Tripo — mismos 215.130 vértices
y mismas 430.209 caras. Las versiones v8–v11 solo tocaron el cuerpo y el cuello.

## Malla completa

| | Valor |
|---|---|
| Vértices | 364.823 |
| Caras | 731.570 |
| Densidad media | 2.717 caras/cm² |
| Arista mediana | 0,172 mm |
| Aristas abiertas | **0** |
| Caras degeneradas | **0** |
| Aristas non-manifold | **864** |
| Islas | **2** |

### Sobre esos dos defectos

- Las **864 aristas non-manifold** vienen del v7 original de Tripo, no de los parches.
  El 82 % están por debajo de z=100, o sea **en el cuerpo**. Blender las cuenta como 0
  porque parte los vértices por costura de UV y de material; lo que ve el laminador es
  la topología soldada por posición, y ahí están.
- La **segunda isla** son 12 caras sueltas a z = 128,70–128,71: una lasca plana de
  0,04 mm sobrante del parche del cuello. Por debajo del vóxel del WJP — no justifica
  volver a subir el fichero.

## Otras comprobaciones sobre este mismo fichero

- Sección mínima del cuello: **231,2 mm²** (era 179,3 en el v7 → **+29 %**)
- Pared fina: riesgo **aceptado** por escrito ante JLC. El pelo y las gafas se imprimen
  tal cual, sin engordar — es el retrato de una persona real.
- Transparencia por debajo de 1,7 mm: aceptada. El único color saturado es la lente
  ámbar de las gafas, donde el efecto translúcido queda bien.
- Material huérfano de verdad (a más de 1,5 mm de cualquier punto con 1 mm de espesor):
  4,4 mm³ de 7.617 en el pelo = **0,06 %**. No es un pelo fino: son cuatro pelillos sueltos.

---

*Medido con `score_head.py` y `ref_cara.py` sobre el fichero real enviado, no sobre una copia.*
