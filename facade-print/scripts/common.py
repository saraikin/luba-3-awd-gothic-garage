from __future__ import annotations
import base64, io, json, math
from pathlib import Path
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def load_asset(path: Path) -> Image.Image:
    if path.exists():
        return Image.open(path).convert('RGB')
    chunks = sorted(path.parent.glob(path.name + '.b64.*'))
    if not chunks:
        raise FileNotFoundError(path)
    raw = base64.b64decode(''.join(p.read_text(encoding='ascii').strip() for p in chunks))
    return Image.open(io.BytesIO(raw)).convert('RGB')


def mm_to_px(mm: float, dpi: int) -> int:
    return int(round(mm / 25.4 * dpi))


def mm_to_pt(mm: float) -> float:
    return mm / 25.4 * 72.0


def pointed_path(cx: float, top: float, width: float, height: float, arch: float) -> str:
    left, right, spring, bottom = cx-width/2, cx+width/2, top+arch, top+height
    return (f'M {left:.3f},{bottom:.3f} L {left:.3f},{spring:.3f} '
            f'Q {left:.3f},{top+arch*.42:.3f} {cx:.3f},{top:.3f} '
            f'Q {right:.3f},{top+arch*.42:.3f} {right:.3f},{spring:.3f} '
            f'L {right:.3f},{bottom:.3f} Z')


def pointed_mask(size: tuple[int,int], cx_mm: float, top_mm: float, width_mm: float,
                 height_mm: float, arch_mm: float, dpi: int) -> Image.Image:
    import numpy as np
    mask = Image.new('L', size, 0); d = ImageDraw.Draw(mask)
    cx, top, width, height, arch = [mm_to_px(v,dpi) for v in (cx_mm,top_mm,width_mm,height_mm,arch_mm)]
    left, right, spring, bottom = cx-width//2, cx+width//2, top+arch, top+height
    pts=[(left,bottom),(left,spring)]
    for t in np.linspace(0,1,36):
        p=(1-t)**2*np.array([left,spring])+2*(1-t)*t*np.array([left,top+arch*.42])+t*t*np.array([cx,top])
        pts.append(tuple(p.astype(int)))
    for t in np.linspace(0,1,36):
        p=(1-t)**2*np.array([cx,top])+2*(1-t)*t*np.array([right,top+arch*.42])+t*t*np.array([right,spring])
        pts.append(tuple(p.astype(int)))
    pts.append((right,bottom)); d.polygon(pts, fill=255)
    return mask


def entrance_geometry(cfg: dict) -> tuple[str, dict]:
    w=cfg['wall']; e=cfg['entrance']; seg=w['segments_mm']
    front_start=seg[0]+seg[1]; cx=front_start+seg[2]/2
    bottom=w['height_mm']; top=bottom-e['height_mm']; spring=top+e['corner_radius_mm']
    lt=cx-e['top_width_mm']/2; rt=cx+e['top_width_mm']/2
    lb=cx-e['bottom_width_mm']/2; rb=cx+e['bottom_width_mm']/2; r=e['corner_radius_mm']
    path=(f'M {lb:.3f},{bottom:.3f} L {lt:.3f},{spring:.3f} '
          f'A {r:.3f},{r:.3f} 0 0 1 {lt+r:.3f},{top:.3f} '
          f'L {rt-r:.3f},{top:.3f} A {r:.3f},{r:.3f} 0 0 1 {rt:.3f},{spring:.3f} '
          f'L {rb:.3f},{bottom:.3f} Z')
    return path, dict(cx=cx,top=top,spring=spring,lt=lt,rt=rt,lb=lb,rb=rb,r=r,bottom=bottom)


def entrance_mask(size: tuple[int,int], cfg: dict, dpi: int) -> Image.Image:
    _,g=entrance_geometry(cfg); m=Image.new('L',size,0); d=ImageDraw.Draw(m)
    px=lambda v:mm_to_px(v,dpi); r=px(g['r'])
    lt,rt,lb,rb,top,spring=[px(g[k]) for k in ('lt','rt','lb','rb','top','spring')]
    d.rectangle([lt+r,top,rt-r,size[1]],fill=255); d.rectangle([lb,spring,rb,size[1]],fill=255)
    d.rectangle([lt,spring,rt,size[1]],fill=255)
    d.pieslice([lt,top,lt+2*r,top+2*r],180,270,fill=255)
    d.pieslice([rt-2*r,top,rt,top+2*r],270,360,fill=255)
    return m


def image_pdf(image: Path, pdf: Path, width_mm: float, height_mm: float, title: str) -> None:
    c=canvas.Canvas(str(pdf),pagesize=(mm_to_pt(width_mm),mm_to_pt(height_mm)),pageCompression=1,invariant=1)
    c.setTitle(title); c.drawImage(ImageReader(str(image)),0,0,width=mm_to_pt(width_mm),height=mm_to_pt(height_mm),preserveAspectRatio=False)
    c.showPage(); c.save()


def data_uri(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode('ascii')
