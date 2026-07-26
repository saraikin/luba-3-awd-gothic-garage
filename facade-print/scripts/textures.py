from __future__ import annotations
import random, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from common import mm_to_px, pointed_mask, entrance_geometry

STONE=[(91,82,74),(108,96,83),(123,107,91),(76,72,68),(135,115,95),(101,91,82)]
WOOD=[(104,64,38),(116,72,41),(92,57,35),(126,78,43),(110,67,38)]


def _noise(size, base, seed, strength=12):
    rng=np.random.default_rng(seed); a=np.empty((size[1],size[0],3),dtype=np.int16); a[:]=base
    a=np.clip(a+rng.normal(0,strength,(size[1],size[0],1)),0,255).astype('uint8')
    return Image.fromarray(a,'RGB').filter(ImageFilter.GaussianBlur(.55))


def generate_wall(cfg: dict) -> Image.Image:
    """Deterministic realistic-style small-stone wall and architectural surrounds."""
    dpi=cfg['dpi']; w=cfg['wall']; win=cfg['windows']; seed=cfg['random_seed']; rng=random.Random(seed)
    mw=2200; scale=mw/w['width_mm']; mh=round(w['height_mm']*scale); sx=scale; sy=scale
    render_dpi=25.4*scale
    im=_noise((mw,mh),(50,47,44),seed,7); d=ImageDraw.Draw(im,'RGBA')
    y=0; row=0
    while y<mh:
        h=rng.randint(max(9,round(38*sy)),max(13,round(57*sy))); x=-rng.randint(0,45) if row%2 else 0
        while x<mw:
            ww=rng.randint(max(25,round(85*sx)),max(45,round(150*sx))); gap=max(2,round(4*sx)); j=2
            pts=[(x+rng.randint(-j,j),y+rng.randint(-j,j)),(x+ww+rng.randint(-j,j),y+rng.randint(-j,j)),(x+ww+rng.randint(-j,j),y+h+rng.randint(-j,j)),(x+rng.randint(-j,j),y+h+rng.randint(-j,j))]
            col=tuple(max(0,min(255,c+rng.randint(-8,8))) for c in rng.choice(STONE))
            d.polygon(pts,fill=col+(255,),outline=(37,34,32,245)); d.line(pts[:2],fill=(226,206,181,35),width=1)
            if rng.random()<.18:
                cx=x+ww*.45; cy=y+h*.35; d.line([(cx,cy),(cx+rng.randint(-6,6),cy+rng.randint(4,8)),(cx+rng.randint(-5,5),cy+rng.randint(10,15))],fill=(27,25,23,110),width=1)
            x+=ww+gap
        y+=h+max(2,round(4*sy)); row+=1
    d.rectangle([0,0,mw,round(w['top_fold_mm']*sy)],fill=(35,32,30,75))

    def quoin(cx_mm,width_mm=82):
        cx=cx_mm*sx; yy=w['top_fold_mm']*sy; i=0
        while yy<mh:
            hh=(52 if i%2==0 else 62)*sy; ww=(width_mm+(18 if i%2 else 0))*sx
            d.rectangle([cx-ww/2,yy,cx+ww/2,min(mh,yy+hh-2)],fill=((132,113,95,245) if i%2==0 else (105,94,84,245)),outline=(43,39,36,230),width=1); yy+=hh; i+=1

    seg=w['segments_mm']; corners=[]; acc=0
    for s in seg[:4]: acc+=s; corners.append(acc)
    for x in corners: quoin(x)

    def buttress(cx_mm,width_mm=105):
        cx=cx_mm*sx; top=w['top_fold_mm']*sy; bottom=mh
        d.polygon([(cx-width_mm*sx/2,top),(cx+width_mm*sx/2,top),(cx+width_mm*sx*.68,bottom),(cx-width_mm*sx*.68,bottom)],fill=(82,74,68,245),outline=(35,32,30,255))
        yy=top+3; i=0
        while yy<bottom:
            hh=54*sy; spread=1+(yy-top)/(bottom-top)*.24; ww=width_mm*sx*spread
            d.rectangle([cx-ww/2+2,yy,cx+ww/2-2,min(bottom,yy+hh-2)],fill=((119,103,89,245) if i%2==0 else (94,85,78,245)),outline=(45,41,38,220),width=1); yy+=hh; i+=1

    wrap_end=sum(seg[:-1])
    buttress(0,88)
    for x in corners: buttress(x,105)
    buttress(wrap_end,88)

    _,g=entrance_geometry(cfg); border=58; r=g['r']+border; left=g['lt']-border; right=g['rt']+border; top=g['top']-border
    d.rounded_rectangle([left*sx,top*sy,right*sx,mh+30],radius=r*min(sx,sy),fill=(91,78,67,255),outline=(40,36,33,255),width=2)

    # The frame is a dilation of the exact opening mask. This guarantees that the
    # later cut contour is concentric with the printed frame at both window positions.
    frame_mm=win.get('frame_width_mm',18.0)
    frame_px=max(1,round(frame_mm*scale)); filter_size=frame_px*2+1
    for cx in win['centers_x_mm']:
        opening=pointed_mask((mw,mh),cx,win['top_mm'],win['width_mm'],win['height_mm'],win['arch_height_mm'],render_dpi)
        surround_mask=opening.filter(ImageFilter.MaxFilter(filter_size))
        surround=Image.new('RGB',(mw,mh),(121,104,88)); im.paste(surround,(0,0),surround_mask)
    d=ImageDraw.Draw(im,'RGBA')
    for cx in win['centers_x_mm']:
        x=cx*sx; y=(win['top_mm']+win['height_mm']+10)*sy
        d.polygon([(x-(win['width_mm']/2+frame_mm+2)*sx,y),(x+(win['width_mm']/2+frame_mm+2)*sx,y),(x+(win['width_mm']/2+frame_mm-4)*sx,y+9),(x-(win['width_mm']/2+frame_mm-4)*sx,y+9)],fill=(132,112,94,255),outline=(44,40,37,220))

    moss=Image.new('RGBA',(mw,mh),(0,0,0,0)); md=ImageDraw.Draw(moss,'RGBA')
    for _ in range(900):
        x=rng.randrange(mw); y=mh-abs(int(rng.gauss(8,18))); rr=rng.randint(1,5); md.ellipse([x-rr,y-rr,x+rr,y+rr],fill=rng.choice([(48,66,31,35),(74,80,40,28),(31,47,27,30)]))
    im=Image.alpha_composite(im.convert('RGBA'),moss.filter(ImageFilter.GaussianBlur(2))).convert('RGB')

    final=im.resize((mm_to_px(w['width_mm'],dpi),mm_to_px(w['height_mm'],dpi)),Image.Resampling.LANCZOS)
    overlap_px=mm_to_px(seg[-1],dpi); wrap_end_px=mm_to_px(wrap_end,dpi)
    if overlap_px>0:
        final.paste(final.crop((0,0,overlap_px,final.height)),(wrap_end_px,0))
    return final


def generate_wood_piece(width_px: int, height_px: int, seed: int, dpi: float) -> Image.Image:
    """Create one plank piece at its final physical scale; no narrow source strip is stretched."""
    rng=random.Random(seed); width_px=max(2,width_px); height_px=max(2,height_px)
    base=rng.choice(WOOD); im=_noise((width_px,height_px),base,seed,8); d=ImageDraw.Draw(im,'RGBA')
    px_per_mm=dpi/25.4
    grain_spacing_px=max(5,round(rng.uniform(2.2,3.4)*px_per_mm)); line_width=max(1,round(.22*px_per_mm)); step=max(12,round(16*px_per_mm))
    for x0 in range(rng.randint(-grain_spacing_px,0),width_px+grain_spacing_px,grain_spacing_px):
        phase=rng.random()*math.tau; amp=rng.uniform(.35,.9)*px_per_mm; drift=rng.uniform(-.012,.012); pts=[]
        for y in range(-step,height_px+step,step):
            x=x0+math.sin(y/max(1,55*px_per_mm)+phase)*amp+drift*y+rng.uniform(-.25,.25)*px_per_mm
            pts.append((x,y))
        d.line(pts,fill=(48,28,17,rng.randint(45,90)),width=line_width)
        if rng.random()<.35:
            d.line([(x+max(1,round(.8*px_per_mm)),y) for x,y in pts],fill=(205,145,91,rng.randint(18,38)),width=1)
    for _ in range(max(1,round(width_px/max(1,16*px_per_mm)))):
        x=rng.randrange(width_px); shade=rng.choice([(38,22,14,18),(210,150,96,15)])
        d.rectangle([x,0,min(width_px,x+max(1,round(rng.uniform(.5,1.8)*px_per_mm))),height_px],fill=shade)
    length_mm=height_px/px_per_mm
    knot_count=0 if length_mm<150 and rng.random()<.6 else rng.choices([0,1,2],[.35,.5,.15])[0]
    margin=max(2,min(height_px//3,round(15*px_per_mm)))
    for _ in range(knot_count):
        x=rng.randint(max(1,width_px//5),max(1,width_px-width_px//5)); y=rng.randint(margin,max(margin,height_px-margin))
        rx=max(2,round(rng.uniform(1.2,2.6)*px_per_mm)); ry=max(3,round(rng.uniform(3.0,7.0)*px_per_mm))
        d.ellipse([x-rx,y-ry,x+rx,y+ry],fill=(50,29,17,95),outline=(35,20,13,150),width=max(1,round(.25*px_per_mm)))
        d.ellipse([x-rx*.45,y-ry*.45,x+rx*.45,y+ry*.45],fill=(35,20,13,100))
    im=ImageEnhance.Contrast(im).enhance(1.08)
    return ImageEnhance.Brightness(im).enhance(rng.uniform(.9,1.1))
