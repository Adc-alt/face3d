"""Recorta la foto a la cabeza y la deja cuadrada a 1024 para los generadores.
Landmarks leidos sobre la rejilla (grid.png), en px del original 354x472."""
import sys
from PIL import Image

SRC = sys.argv[1] if len(sys.argv) > 1 else '/mnt/c/Users/adelg/Pictures/unnamed.jpg'
PELO, BARBILLA, EJE_X = 62, 310, 160        # alto del pelo, barbilla, eje de la cara

im = Image.open(SRC).convert('RGB')
W, H = im.size
cy = (PELO + BARBILLA) / 2

for tag, lado, cx, cyy in (('A_cabeza', 285, EJE_X, cy),
                           ('B_busto',  354, 177,   cy + 30)):
    lado = min(lado, W, H)
    x = min(max(cx - lado / 2, 0), W - lado)
    y = min(max(cyy - lado / 2, 0), H - lado)
    out = im.crop((round(x), round(y), round(x + lado), round(y + lado)))
    out.resize((1024, 1024), Image.LANCZOS).save(f'crop_{tag}.png')
    print(f'crop_{tag}.png  <- {int(lado)}x{int(lado)} px reales, cabeza ocupa '
          f'{100*(BARBILLA-PELO)/lado:.0f}% del alto')
