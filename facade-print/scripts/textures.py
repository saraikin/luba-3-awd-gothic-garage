from __future__ import annotations
import random, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from common import mm_to_px, pointed_mask, entrance_geometry

STONE=[(91,82,74),(108,96,83),(123,107,91),(76,72,68),(135,115,95),(101,91,82)]


def _noise(size, base, seed, strength=12):
    rng=np.random.default_rng(seed); a=np.empty((size[1],size[0],3),dtype=np.int16); a[:]=base
    a=np.clip(a+rng.normal(0,strength,(size[1],size[0],1)),0,255).astype('uint8')
    return Image.fromarray(a,'RGB').filter(ImageFilter.GaussianBlur(.55))


def generate_wall(cfg: dict) -> Image.Image:
    """Deterministic realistic-style small-stone wall and architectural surrounds."""
    dpi=cfg['dpi']; w=cfg['wall']; win=cfg['windows']; seed=cfg['random_seed']; rng=random.Random(seed)
    mw=2200; mh=round(mw*w['height_mm']/w['width_mm']); sx=mw/w['width_mm']; sy=mh/w['height_mm']
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

    for x in (42,w['width_mm']-42,seg[0],seg[0]+seg[1],seg[0]+seg[1]+seg[2],seg[0]+seg[1]+seg[2]+seg[3]): buttress(x,88 if x in (42,w['width_mm']-42) else 105)
    _,g=entrance_geometry(cfg); border=58; r=g['r']+border; left=g['lt']-border; right=g['rt']+border; top=g['top']-border
    d.rounded_rectangle([left*sx,top*sy,right*sx,mh+30],radius=r*min(sx,sy),fill=(91,78,67,255),outline=(40,36,33,255),width=2)
    for cx in win['centers_x_mm']:
        mask=pointed_mask((mw,mh),cx,win['top_mm']-15,win['width_mm']+34,win['height_mm']+30,win['arch_height_mm']+22,round(25.4*sx))
        surround=Image.new('RGB',(mw,mh),(121,104,88)); im.paste(surround,(0,0),mask); d=ImageDraw.Draw(im,'RGBA')
    for cx in win['centers_x_mm']:
        x=cx*sx; y=(win['top_mm']+win['height_mm']+10)*sy; d.polygon([(x-(win['width_mm']/2+20)*sx,y),(x+(win['width_mm']/2+20)*sx,y),(x+(win['width_mm']/2+14)*sx,y+9),(x-(win['width_mm']/2+14)*sx,y+9)],fill=(132,112,94,255),outline=(44,40,37,220))
    moss=Image.new('RGBA',(mw,mh),(0,0,0,0)); md=ImageDraw.Draw(moss,'RGBA')
    for _ in range(900):
        x=rng.randrange(mw); y=mh-abs(int(rng.gauss(8,18))); rr=rng.randint(1,5); md.ellipse([x-rr,y-rr,x+rr,y+rr],fill=rng.choice([(48,66,31,35),(74,80,40,28),(31,47,27,30)]))
    im=Image.alpha_composite(im.convert('RGBA'),moss.filter(ImageFilter.GaussianBlur(2))).convert('RGB')
    return im.resize((mm_to_px(w['width_mm'],dpi),mm_to_px(w['height_mm'],dpi)),Image.Resampling.LANCZOS)


def generate_wood(cfg: dict) -> Image.Image:
    """Deterministic aged-wood source texture sampled by the floor generator."""
    seed=cfg['random_seed']+101; rng=random.Random(seed); width,height=500,700
    im=_noise((width,height),(105,63,35),seed,14); d=ImageDraw.Draw(im,'RGBA')
    for _ in range(90):
        x=rng.randrange(width); pts=[]; y=-20
        while y<height+20: pts.append((x+rng.randint(-5,5),y)); y+=rng.randint(28,70)
        d.line(pts,fill=(42,25,16,rng.randint(35,75)),width=rng.choice([1,1,2]))
    for _ in range(18):
        x=rng.randint(15,width-15); y=rng.randint(20,height-20); rx=rng.randint(5,13); ry=rng.randint(9,25)
        d.ellipse([x-rx,y-ry,x+rx,y+ry],outline=(40,23,14,145),width=2); d.ellipse([x-rx/2,y-ry/2,x+rx/2,y+ry/2],fill=(40,23,14,80))
    return ImageEnhance.Contrast(im).enhance(1.08)
