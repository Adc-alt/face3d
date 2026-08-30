#!/usr/bin/env python3
"""45 generaciones (3 modelos × 1 foto × 5 semillas) + scoring."""
import os
import sys
import json
import subprocess
import cv2
import numpy as np
from pathlib import Path
from tqdm import tqdm
from datetime import datetime

# Asumir que score_head.py y likeness.py están en /root/
sys.path.insert(0, '/root')

PHOTO = '/root/crop_A_cabeza_nobg.png'
OUT_DIR = '/root/benchmark_outputs'
RESULTS_CSV = f'{OUT_DIR}/resultados_benchmark.json'

os.makedirs(OUT_DIR, exist_ok=True)

# Importar scorers
try:
    import score_head
    import likeness
except ImportError as e:
    print(f"ERROR: Falta {e.name}. Sube score_head.py y likeness.py a /root/")
    sys.exit(1)

if not os.path.exists(PHOTO):
    print(f"ERROR: Falta {PHOTO}")
    sys.exit(1)

print(f"Foto: {PHOTO}")
print(f"Outputs: {OUT_DIR}")
print(f"Timestamp: {datetime.now().isoformat()}\n")

results = []

# ============================================================================
# TRELLIS.2-4B
# ============================================================================
print("=" * 60)
print("TRELLIS.2-4B (5 seeds)")
print("=" * 60)

trellis_out = f'{OUT_DIR}/trellis'
os.makedirs(trellis_out, exist_ok=True)

for seed in range(5):
    name = f'trellis_seed{seed}'
    out_path = f'{trellis_out}/{name}'
    os.makedirs(out_path, exist_ok=True)

    try:
        # TRELLIS.2 CLI: python -m trellis.pipelines generate-mesh --input img --output-dir out [--seed N]
        cmd = [
            'python', '-m', 'trellis.pipelines', 'generate-mesh',
            '--input', PHOTO,
            '--output-dir', out_path,
            '--seed', str(seed),
        ]
        print(f"[{name}] Ejecutando TRELLIS.2...")
        subprocess.run(cmd, check=True, capture_output=True, cwd='/root/trellis')

        # Buscar mesh generado (típicamente meshes/model.obj)
        mesh_paths = list(Path(out_path).glob('**/model.obj')) + list(Path(out_path).glob('**/*.obj'))
        if not mesh_paths:
            print(f"  ⚠ No mesh generado")
            continue

        mesh = str(mesh_paths[0])
        print(f"  ✓ Malla: {mesh}")

        # Score imprimibilidad
        try:
            imp_score = score_head.score_file(mesh)
            print(f"  Imprimibilidad: {imp_score}")
        except Exception as e:
            print(f"  ⚠ Score imprimibilidad falló: {e}")
            imp_score = None

        # Score parecido
        try:
            app = likeness.FaceAnalysis(name='buffalo_l')
            app.prepare(ctx_id=-1, det_size=(320, 320))
            lik_score = likeness.parecido(app, PHOTO, mesh)
            print(f"  Parecido: {lik_score:.3f}" if lik_score else "  Parecido: No detectado")
        except Exception as e:
            print(f"  ⚠ Score parecido falló: {e}")
            lik_score = None

        results.append({
            'model': 'TRELLIS.2-4B',
            'seed': seed,
            'mesh': mesh,
            'imprimibilidad': imp_score,
            'parecido': lik_score,
            'timestamp': datetime.now().isoformat(),
        })

    except Exception as e:
        print(f"  ERROR: {e}")

# ============================================================================
# TripoSG
# ============================================================================
print("\n" + "=" * 60)
print("TripoSG (5 seeds)")
print("=" * 60)

tripo_out = f'{OUT_DIR}/tripo'
os.makedirs(tripo_out, exist_ok=True)

for seed in range(5):
    name = f'tripo_seed{seed}'
    out_path = f'{tripo_out}/{name}'
    os.makedirs(out_path, exist_ok=True)

    try:
        # TripoSG CLI similar a TRELLIS
        cmd = [
            'python', '-m', 'tripo.cli',
            '--input', PHOTO,
            '--output-dir', out_path,
            '--seed', str(seed),
        ]
        print(f"[{name}] Ejecutando TripoSG...")
        subprocess.run(cmd, check=True, capture_output=True, cwd='/root/tripo')

        mesh_paths = list(Path(out_path).glob('**/model.obj')) + list(Path(out_path).glob('**/*.obj'))
        if not mesh_paths:
            print(f"  ⚠ No mesh generado")
            continue

        mesh = str(mesh_paths[0])
        print(f"  ✓ Malla: {mesh}")

        try:
            imp_score = score_head.score_file(mesh)
            print(f"  Imprimibilidad: {imp_score}")
        except Exception as e:
            print(f"  ⚠ Score imprimibilidad falló: {e}")
            imp_score = None

        try:
            app = likeness.FaceAnalysis(name='buffalo_l')
            app.prepare(ctx_id=-1, det_size=(320, 320))
            lik_score = likeness.parecido(app, PHOTO, mesh)
            print(f"  Parecido: {lik_score:.3f}" if lik_score else "  Parecido: No detectado")
        except Exception as e:
            print(f"  ⚠ Score parecido falló: {e}")
            lik_score = None

        results.append({
            'model': 'TripoSG',
            'seed': seed,
            'mesh': mesh,
            'imprimibilidad': imp_score,
            'parecido': lik_score,
            'timestamp': datetime.now().isoformat(),
        })

    except Exception as e:
        print(f"  ERROR: {e}")

# ============================================================================
# EMOCA (control — sparse, puede fallar)
# ============================================================================
print("\n" + "=" * 60)
print("EMOCA (5 seeds) — control sparse mesh")
print("=" * 60)

emoca_out = f'{OUT_DIR}/emoca'
os.makedirs(emoca_out, exist_ok=True)

for seed in range(5):
    name = f'emoca_seed{seed}'
    print(f"[{name}] EMOCA requiere setup adicional (omitido por ahora)")

# ============================================================================
# Guardar resultados
# ============================================================================
print("\n" + "=" * 60)
print(f"Guardando resultados en {RESULTS_CSV}")
print("=" * 60)

with open(RESULTS_CSV, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n✓ Benchmark completado: {len(results)} generaciones")
print(f"  Resultados en: {RESULTS_CSV}")

# Resumen
if results:
    df_like = [r['parecido'] for r in results if r['parecido'] is not None]
    if df_like:
        print(f"\n  Parecido medio: {np.mean(df_like):.3f}")
        print(f"  Parecido max: {max(df_like):.3f} (mejor)")
        print(f"  Parecido min: {min(df_like):.3f}")
