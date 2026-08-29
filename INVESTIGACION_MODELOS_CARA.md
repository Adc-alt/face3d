# Cara 3D a partir de una foto — investigación de modelos y plan de decisión

Fecha: 2026-08-29 · Proyecto: figurina personalizada a partir de una sola foto
Estado: **investigación cerrada, ejecución pendiente**

---

## 1. Qué estamos decidiendo exactamente

No estamos eligiendo "el mejor modelo 3D". Estamos eligiendo **quién genera la cabeza**,
sabiendo que:

- el cuerpo lo vamos a hacer nosotros (biblioteca paramétrica propia, fase posterior),
- la unión cabeza↔cuerpo, la reparación, el escalado a 170 mm y el print-prep son nuestros pase lo que pase,
- y que el fallo histórico no fue estético: fue **malla**. La v7 de Tripo (y por herencia
  la v8–v11) traía 864 aristas non-manifold reales, el 82 % de ellas por debajo de z=100,
  o sea **en el cuerpo, no en la cara**.

Ese dato es el que justifica todo este documento: si generamos **solo la cabeza**, quitamos
de un plumazo el 82 % del daño topológico y ganamos resolución en lo único que el cliente
va a mirar de cerca.

### Criterio de éxito (dos números, no opiniones)

| Métrica | Cómo se mide | Umbral para aceptar |
|---|---|---|
| **Imprimibilidad** | `score_head.py` (ya construido y validado) | 0 aristas abiertas, 0 non-manifold, 1 isla, volumen > 0, llena_bbox < 95 % |
| **Parecido** | coseno de embedding facial entre la foto original y un render frontal de la malla | por definir tras la primera ronda; se fija con el resultado bueno de Tripo como referencia |

Y una tercera condición que no es una métrica sino una regla: **con semilla fija, dos
ejecuciones iguales deben dar la misma malla.** Tripo acertó 1 de 5. Eso no es calidad,
es varianza. Un modelo que acierta 3 de 5 pero de forma reproducible vale más que uno
que acierta 1 de 5 por lotería.

---

## 2. El hallazgo principal de la investigación

**Hay dos familias de modelos y no compiten: se complementan.** Casi toda la comparativa
que circula por internet mezcla las dos y por eso no sirve para nuestro caso.

### Familia A — generativos de objeto genérico
*TRELLIS.2, Hunyuan3D, TripoSG, Sparc3D, Direct3D-S2, y el Tripo comercial que usaste.*

Ven una imagen y sacan un objeto. **No saben que están mirando una cara.** Para ellos un
retrato y una silla son el mismo problema.

- ✅ Te dan pelo, gafas, orejas, hombros, estilo — todo en una pasada.
- ❌ El parecido es un subproducto estadístico. No hay nada en el modelo que penalice
  "esta cara no es la de la foto". **Por eso Tripo tuvo esa varianza.** No fue mala suerte
  tuya: es la naturaleza de la familia.

### Familia B — reconstructores de cara (modelos morfables 3D / 3DMM)
*FLAME + DECA / EMOCA / MICA / TokenFace / Pixel3DMM.*

Llevan dentro un modelo estadístico del cráneo humano. La salida es **siempre la misma
malla**: mismos vértices, misma topología, estanca por construcción.

- ✅ Cero aristas abiertas, cero non-manifold, una sola isla — **siempre, sin trabajo**.
  `score_head.py` les da luz verde de serie.
- ✅ Están entrenados y evaluados **explícitamente contra métricas de parecido**
  (benchmark NoW del Max Planck). Es decir: la identidad no es un accidente, es el objetivo.
- ❌ Cabeza calva, sin gafas, sin estilo, geometría "de laboratorio".

### La conclusión

**Ninguna familia sola resuelve el problema.** La respuesta es híbrida, y es precisamente
la parte que nos hace dueños de la tubería:

```
foto → [Familia B] → cráneo FLAME estanco = ANCLA DE IDENTIDAD + ANCLA DE TOPOLOGÍA
                          ↓
     → [Familia A] → cabeza con pelo, gafas y estilo
                          ↓
     → comparar A contra B: ¿se ha inventado la cara el generativo?
                          ↓
                  aceptar / rechazar automáticamente
```

Eso convierte *"salió bien una vez"* en **un test automático de rechazo**. Generamos 5,
medimos la distancia al ancla FLAME, y nos quedamos con la mejor. Es la respuesta directa
a tu pregunta de si el camino abierto puede ser tan fiel como Tripo: **puede ser más fiel,
no porque el modelo sea mejor, sino porque nosotros podemos medir y descartar, y Tripo no
te dejaba hacer ni una cosa ni la otra.**

Nota útil: **EMOCA ya está instalado en tu máquina** (`~/emoca`), y es de Familia B.
Ese trozo no hay que comprarlo.

---

## 3. Candidatos, con licencia verificada

| Modelo | Familia | Licencia | VRAM | Topología cruda | Veredicto |
|---|---|---|---|---|---|
| **TRELLIS.2-4B** (Microsoft, dic-2025, 4 B parám.) | A | **MIT**, sin restricciones | 24 GB mín. | O-Voxel *field-free*: admite superficies abiertas → **puede traer agujeros**, el propio repo trae scripts de relleno | **Candidato nº 1.** Líder de calidad entre los abiertos. 512³/1024³/1536³ |
| **TripoSG** (VAST-AI, la empresa de Tripo) | A | **MIT** | ~8 GB | SDF + marching cubes → **estanco por construcción** | **Candidato nº 2.** Es el hermano abierto del que te gustó |
| **Hunyuan3D 2.1 / 3.x** (Tencent) | A | Community License: **excluye UE, Reino Unido y Corea — incluidos los *outputs*** | 10–29 GB | SDF → estanco | **DESCARTADO.** Bloqueo legal, no técnico. Ni el modelo ni lo que produce se pueden usar desde España |
| **Sparc3D** | A | repo abierto pero el proyecto pivotó a la plataforma de pago Hitem3D | alta | 1024³, estanco | Reserva. Riesgo de proyecto |
| **Direct3D-S2** | A | abierto | alta | entrenado sobre mallas watertight | Reserva |
| **TripoSR** | A | MIT | 6 GB | rápido (<1 s) pero baja fidelidad | Solo para iterar rápido, no para producción |
| **EMOCA / DECA** (FLAME) | B | ⚠️ **investigación, no comercial** | 4 GB — corre en tu portátil | estanca siempre | Ancla de identidad. **Ver riesgo legal abajo** |
| **MICA / TokenFace / Pixel3DMM** | B | varía por repo | baja | estanca siempre | Mejor identidad medida en NoW. Alternativas al ancla |

### ⚠️ Riesgo legal abierto (no resuelto)

FLAME (Max Planck) se distribuye **para investigación no comercial**. Todos los modelos de
Familia B que hemos listado lo usan por debajo. Lo mismo pasa con los pesos preentrenados
de reconocimiento facial (InsightFace/ArcFace) que necesitaríamos para la métrica de parecido:
el código es abierto, **los pesos suelen ser no comerciales**.

No es un problema para investigar y medir. **Sí lo es para vender.** Salidas posibles,
por orden de esfuerzo:
1. Licencia comercial de FLAME al Max Planck (existe, se pide y se paga).
2. Usar Familia B solo como herramienta interna de validación durante el desarrollo y no
   embarcarla en el producto — *jurídicamente flojo, hay que consultarlo*.
3. Sustituir el ancla por un modelo morfable de licencia limpia.

**Acción: verificar esto antes de facturar el primer euro, no antes de la primera prueba.**

---

## 4. Sobre por qué ir a código abierto — corrección honesta

Tu hipótesis era que sale más rentable hacerlo nosotros. **Con los números en la mano,
el dinero no es el argumento:**

- API de Tripo: 0,10–0,35 € por generación. API de Rodin: ~0,40 €.
- 10.000 figurinas al año = **3.500 € de API**. Menos de lo que cuesta el tiempo de
  ingeniería de mantener una tubería propia.

**El argumento real es el control, y es un argumento fuerte:**

1. **Semilla fija y reproducibilidad.** Con API no puedes fijar el azar. Es lo que te pasó.
2. **Te saltas su post-proceso.** Las 864 aristas non-manifold no las creó el modelo de
   forma: las creó el remallado, la conversión a quads, el desplegado de UV y la
   decimación que el proveedor aplica al final. Corriendo el repo tú, **esa etapa
   simplemente no existe**, y sale la malla del marching cubes, limpia.
3. **Puedes meter pasos tuyos en medio** — el ancla de identidad, el filtrado de grosor
   mínimo, el corte del cuello — cosa imposible detrás de una API.
4. **Sin dependencia de precio ni de que cierren el grifo.** Ya te pasó con Tripo.

Vamos a abierto por 2 y 3, no por el precio. Conviene tenerlo claro para no defender el
camino por la razón equivocada.

---

## 5. Plan A — camino abierto

### Fase 0 · Preparar la entrada *(no requiere GPU — es donde más se gana)*
La cabeza de tu foto medía **248 px**. Ningún modelo inventa detalle que no está.
- [x] recorte de cabeza y de busto (`crop.py`)
- [x] fondo quitado a RGBA (`quitafondo.py`) — el cubo negro de Hunyuan salió por meter
      una imagen opaca de borde a borde: el modelo esculpió el marco
- [ ] **conseguir de 3 a 5 fotos de partida mejores, frontales, con la cara ≥ 800 px**

### Fase 1 · Banco de pruebas
Alquilar una 4090 (RunPod / Vast, ~0,35 €/h). Correr los **repos reales**, no demos web.

- 3 modelos (TRELLIS.2, TripoSG, +1 reserva) × 5 fotos × 3 semillas = **45 generaciones**
- Tiempo estimado ~2 h → **coste por debajo de 1 €**
- Cada GLB pasa por `score_head.py` y por el medidor de parecido
- Se guarda todo en una tabla: modelo, semilla, resolución, las dos métricas

### Fase 2 · Decisión
- **Sigue el camino abierto** si algún modelo saca ≥ 3 de 5 aceptables **de forma reproducible**.
- **Se corta** si el mejor abierto queda claramente por debajo del resultado bueno de Tripo
  en parecido después de haber probado el ancla de identidad.

### Fase 3 · Tubería propia (solo si la Fase 2 sale bien)
ancla FLAME → generación → aceptar/rechazar automático → limpieza → cuello → escalado 170 mm
→ política de pared mínima → export a JLC.

---

## 6. Plan B — camino de API (el que se abre si la Fase 2 se corta)

**No es el plan del fracaso. Es la etapa de la cara subcontratada, nada más.**

- Candidatos: **Tripo API** (0,10–0,35 €/gen) o **Rodin / Hyper3D** (~0,40 €/gen, licencia
  comercial explícita en plan de pago). Hunyuan queda descartado también aquí, por territorio.
- Cambia **solo la caja que genera la cabeza**. La biblioteca de cuerpos, la unión, la
  reparación, el escalado y el print-prep siguen siendo nuestros.
- Mitigación de la varianza: generar N, medir con nuestras propias métricas, quedarnos
  con la mejor. **La métrica es nuestra aunque el modelo no lo sea** — y es la mitad del
  valor.

---

## 7. Lo que es nuestro pase lo que pase

Conviene tenerlo escrito, porque es donde está el negocio y no depende de qué modelo gane:

1. El preprocesado de la foto (recorte, fondo, encuadre, resolución mínima).
2. Las dos métricas y el filtro automático de aceptación.
3. La biblioteca de cuerpos paramétricos, estancos y con pared ≥ 1 mm por diseño.
4. La unión cabeza↔cuerpo con el cuello preparado.
5. La reparación, el escalado a 170 mm y la preparación de impresión.
6. La relación con JLC y el conocimiento de qué aguanta la resina WJP.

**El generador de caras no lo vamos a entrenar nosotros** — eso son millones y un dataset
que no tenemos. Modelo abierto ajeno, tubería propia.

---

## 8. Registro de resultados *(rellenar en Fase 1)*

| # | Modelo | Foto | Semilla | Res. | abiertas | non-manif. | islas | llena_bbox % | parecido | ¿acepta? |
|---|---|---|---|---|---|---|---|---|---|---|
| — | *(pendiente)* | | | | | | | | | |

**Resultados a día de hoy: ninguno válido.** La única generación existente
(`resultados/hunyuan_A_oct512.glb`) resultó ser un cubo macizo — el modelo esculpió el
marco de la imagen opaca. Descartada.

---

## 9. La referencia a igualar — medida sobre el v7 de Tripo

Objetivo declarado (2026-08-29): **igualar el nivel de detalle de la cara que produjo Tripo
en la v7.** Como tenemos el fichero, esto se convierte en una especificación numérica.
Medido con `ref_cara.py` sobre la banda `z > 136` (la cara protegida):

| | Figura completa | **Solo la cara (z>136)** |
|---|---|---|
| Caras | 654.692 | **430.209** |
| Vértices | 326.382 | 215.130 |
| Área de superficie | 27.380 mm² | 4.069 mm² |
| **Densidad** | 2.391 caras/cm² | **10.573 caras/cm²** |
| **Arista mediana** | 0,192 mm | **0,142 mm** |
| Arista p95 | 0,960 mm | 0,394 mm |
| Dimensiones | 74,4 × 36,6 × 170 mm | **28,8 × 32,6 × 34,0 mm** |

### Lo que dicen estos números

**1. Tripo sí concentró la malla en la cara.** El 66 % de todos los triángulos están en el
15 % del área. La cara tiene 4,4× la densidad del resto. O sea: el problema del v7 **no fue
el reparto de detalle**, fue la varianza entre tiradas y la topología del cuerpo.

**2. La cabeza mide 34 mm.** Ese dato es el que decide toda la estrategia. Un generativo
volumétrico reparte su rejilla sobre el *bounding box* completo. Generando la figura entera,
los 170 mm se comen la rejilla; generando solo la cabeza, los mismos 34 mm reciben
**5× más resolución lineal con el mismo ajuste**:

| | Tripo (figura de 170 mm) | Nosotros (cabeza de 34 mm) |
|---|---|---|
| rejilla 512³ | 0,332 mm/vóxel | **0,066 mm/vóxel** |
| rejilla 1024³ | 0,166 mm/vóxel | **0,033 mm/vóxel** |
| rejilla 1536³ | 0,111 mm/vóxel | **0,022 mm/vóxel** |

Tripo resolvió un detalle efectivo de 0,142 mm. **TRELLIS.2 a 1024³ sobre una cabeza sola
da 0,033 mm — cuatro veces más fino.** Igualar a Tripo no es la meta ambiciosa: es el suelo.

**3. Aviso honesto: densidad de malla ≠ parecido.** 430.000 triángulos pueden ser ruido
denso. Y buena parte de ese detalle de 0,142 mm **no se imprime**: en resina WJP el detalle
geométrico por debajo de ~0,2–0,3 mm no se reproduce, vive en la *textura de color*, no en
la forma. *(Pendiente: confirmar la cifra real con Elinor.)*

### Especificación de aceptación

Una cara nueva se da por buena si cumple **las dos**:

- **Geometría:** ≥ 10.000 caras/cm² sostenidas y arista mediana ≤ 0,15 mm sobre una cabeza
  de ~34 mm, **más** los criterios de `score_head.py` (0 abiertas, 0 non-manifold, 1 isla).
  Esto ya lo bate cualquier generativo moderno corriendo solo sobre la cabeza.
- **Parecido:** ≥ el que saque el propio v7 medido con nuestro mismo medidor.
  **Este es el criterio que de verdad decide**, y es el que aún no está construido.

**El listón geométrico está prácticamente regalado por generar solo la cabeza.
El listón que cuesta es el parecido.**
