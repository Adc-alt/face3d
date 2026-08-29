"""Recorta el fondo y deja PNG con alfa, para pasarselo al generador con
Remove Background DESMARCADO."""
import sys, pathlib
from PIL import Image
from rembg import remove, new_session

ses = new_session('u2net')
for src in sys.argv[1:]:
    p = pathlib.Path(src)
    im = Image.open(p).convert('RGB')
    out = remove(im, session=ses, post_process_mask=True)
    a = out.split()[-1]
    cubre = sum(a.getdata()) / (255 * a.width * a.height)
    dest = p.with_name(p.stem + '_nobg.png')
    out.save(dest)
    print(f"{dest.name}  alfa cubre {cubre*100:.1f}% de la imagen")
