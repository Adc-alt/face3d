#!/bin/bash
set -e

echo "=== Benchmark setup en RunPod A40 ==="

cd /root

# Dependencias base
pip install -q trimesh insightface opencv-python tqdm pillow numpy torch

# TRELLIS.2-4B
echo "Clonando TRELLIS.2..."
if [ ! -d "trellis" ]; then
  git clone https://huggingface.co/JeffreyXiang/TRELLIS trellis
fi
cd trellis
pip install -q -e .
cd ..

# TripoSG
echo "Clonando TripoSG..."
if [ ! -d "tripo" ]; then
  git clone https://huggingface.co/VAST-AI-Research/TripoSR tripo
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
