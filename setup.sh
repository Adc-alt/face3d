#!/bin/bash
set -e

echo "=== Benchmark setup en RunPod A40 ==="

cd /root

# Dependencias base
pip install -q trimesh insightface opencv-python tqdm pillow numpy torch huggingface_hub

# TRELLIS.2-4B
echo "Descargando TRELLIS.2 con snapshot_download..."
if [ ! -d "trellis" ]; then
  python -c "from huggingface_hub import snapshot_download; snapshot_download('JeffreyXiang/TRELLIS', local_dir='trellis')"
fi
cd trellis
pip install -q -e .
cd ..

# TripoSG
echo "Descargando TripoSG con snapshot_download..."
if [ ! -d "tripo" ]; then
  python -c "from huggingface_hub import snapshot_download; snapshot_download('VAST-AI-Research/TripoSR', local_dir='tripo')"
fi
cd tripo
pip install -q -e .
cd ..

# Crear directorio de outputs
mkdir -p /root/benchmark_outputs

echo "✓ Setup completo. Ahora:"
echo "  1. Sube crop_A_cabeza_nobg.png a /root/"
echo "  2. Sube likeness.py y score_head.py a /root/"
echo "  3. Ejecuta: python benchmark.py"
