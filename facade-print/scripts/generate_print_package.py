#!/usr/bin/env python3
from __future__ import annotations
import argparse, random, textwrap
from pathlib import Path
import cairosvg
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
from common import (load_config,load_asset,mm_to_px,mm_to_pt,pointed_path,pointed_mask,
                    entrance_geometry,entrance_mask,image_pdf,data_uri)
from stained_glass import build_svg


def build_wall(cfg,root,out):
    dpi=cfg['dpi']; w=cfg['wall']; win=cfg['windows']; wall=load_asset(root/cfg['assets']['wall_base'])
    wall=wall.resize((mm_to_px(w['width_mm'],dpi),mm_to_px(w['height_mm'],dpi)),Image.Resampling.LANCZOS)
    wall=wall.filter(ImageFilter.UnsharpMask(radius=1.1,percent=115,threshold=2))
    for cx in win['centers_x_mm']:
        wall.paste((255,255,255),(0,0),pointed_mask(wall.size,cx,win['top_mm'],win['width_mm'],win['height_mm'],win['arch_height_mm'],dpi))
    wall.paste((255,255,255),(0,0),entrance_mask(wall.size,cfg,dpi))
    art=out/'wall_stone_with_window_openings.jpg'; wall.save(art,quality=95,subsampling=0,dpi=(dpi,dpi))
    pdf=out/'01_WALLS_STONE_WINDOW_OPENINGS_3875x610mm_100pct.pdf'; image_pdf(art,pdf,w['width_mm'],w['height_mm'],'Luba garage wall film')
    ep,_=entrance_geometry(cfg); windows='\n'.join(f'<path d="{pointed_path(cx,win["top_mm"],win["width_mm"],win["height_mm"],win["arch_height_mm"])}"/>' for cx in win['centers_x_mm'])
    cuts=f'''<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="{w['width_mm']}mm" height="{w['height_mm']}mm" viewBox="0 0 {w['width_mm']} {w['height_mm']}"><g id="ENTRANCE_CUT" fill="none" stroke="#ff00ff" stroke-width=".25"><path d="{ep}"/></g><g id="WINDOW_CUTS" fill="none" stroke="#00a7ff" stroke-width=".25">{windows}</g></svg>'''
    (out/'01B_WALL_CUT_CONTOURS_3875x610mm.svg').write_text(cuts,encoding='utf-8')
    cairosvg.svg2pdf(bytestring=cuts.encode(),write_to=str(out/'01B_WALL_CUT_CONTOURS_3875x610mm.pdf'),output_width=mm_to_pt(w['width_mm']),output_height=mm_to_pt(w['height_mm']))
    bounds=[]; x=0
    for seg in w['segments_mm'][:-1]: x+=seg; bounds.append(x)
    guides=''.join(f'<line x1="{x}" y1="0" x2="{x}" y2="{w["height_mm"]}"/>' for x in bounds)
    hybrid=f'''<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w['width_mm']}mm" height="{w['height_mm']}mm" viewBox="0 0 {w['width_mm']} {w['height_mm']}"><g id="ARTWORK"><image width="{w['width_mm']}" height="{w['height_mm']}" preserveAspectRatio="none" xlink:href="data:image/jpeg;base64,{data_uri(art)}"/></g><g id="ENTRANCE_CUT" style="display:none;fill:none;stroke:#ff00ff;stroke-width:.25"><path d="{ep}"/></g><g id="WINDOW_CUTS" style="display:none;fill:none;stroke:#00a7ff;stroke-width:.25">{windows}</g><g id="PANEL_GUIDES" style="display:none;fill:none;stroke:#777;stroke-width:.18;stroke-dasharray:3,2">{guides}<line x1="0" y1="{w['top_fold_mm']}" x2="{w['width_mm']}" y2="{w['top_fold_mm']}"/></g></svg>'''
    (out/'wall_wrap_hybrid_with_cut_layers.svg').write_text(hybrid,encoding='utf-8')
    return wall


def build_floor(cfg,root,out):
    dpi=cfg['dpi']; f=cfg['floor']; rng=random.Random(cfg['random_seed']); wood=load_asset(root/cfg['assets']['wood_base'])
    size=(mm_to_px(f['file_width_mm'],dpi),mm_to_px(f['file_height_mm'],dpi)); floor=Image.new('RGB',size,(58,37,25)); d=ImageDraw.Draw(floor,'RGBA')
    widths=[]; left=f['trim_width_mm']
    while left>.001:
        x=min(left,rng.uniform(f['plank_width_min_mm'],f['plank_width_max_mm'])); widths.append(x); left-=x
    xmm=f['trim_offset_x_mm']; y0=mm_to_px(f['trim_offset_y_mm'],dpi); y1=mm_to_px(f['trim_offset_y_mm']+f['trim_height_mm'],dpi)
    for i,pw in enumerate(widths):
        x0=mm_to_px(xmm,dpi); x1=mm_to_px(xmm+pw,dpi); sw=rng.randint(max(5,wood.width//100),max(8,wood.width//35)); sx=rng.randint(0,max(0,wood.width-sw))
        strip=wood.crop((sx,0,sx+sw,wood.height)); strip=strip.transpose(Image.Transpose.FLIP_LEFT_RIGHT) if rng.random()<.5 else strip
        strip=strip.resize((max(2,x1-x0),y1-y0),Image.Resampling.LANCZOS); strip=ImageEnhance.Brightness(strip).enhance(rng.uniform(.83,1.12)); floor.paste(strip,(x0,y0))
        d.line([(x0,y0),(x0,y1)],fill=(26,18,13,230),width=max(1,mm_to_px(.75,dpi)))
        fracs=[.28,.58,.82] if i%3==0 else [.37,.72]
        for frac in fracs:
            yy=mm_to_px(f['trim_offset_y_mm']+f['trim_height_mm']*(frac+rng.uniform(-.045,.045)),dpi); d.line([(x0+1,yy),(x1-1,yy)],fill=(27,18,13,235),width=max(1,mm_to_px(.8,dpi)))
            for nx in (x0+max(2,mm_to_px(2.3,dpi)),x1-max(2,mm_to_px(2.3,dpi))):
                r=max(1,mm_to_px(.65,dpi)); d.ellipse([nx-r,yy-r,nx+r,yy+r],fill=(30,28,26,220))
        xmm+=pw
    floor=floor.filter(ImageFilter.UnsharpMask(radius=1,percent=115,threshold=2)); art=out/'attic_floor_fine_planks.jpg'; floor.save(art,quality=95,subsampling=0,dpi=(dpi,dpi))
    image_pdf(art,out/'03_ATTIC_FLOOR_FINE_PLANKS_1004x931mm_100pct.pdf',f['file_width_mm'],f['file_height_mm'],'Luba garage attic floor')
    hybrid=f'''<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{f['file_width_mm']}mm" height="{f['file_height_mm']}mm" viewBox="0 0 {f['file_width_mm']} {f['file_height_mm']}"><image width="{f['file_width_mm']}" height="{f['file_height_mm']}" preserveAspectRatio="none" xlink:href="data:image/jpeg;base64,{data_uri(art)}"/><g id="TRIM_CONTOUR" style="display:none;fill:none;stroke:#ff00ff;stroke-width:.25"><rect x="{f['trim_offset_x_mm']}" y="{f['trim_offset_y_mm']}" width="{f['trim_width_mm']}" height="{f['trim_height_mm']}"/></g></svg>'''; (out/'attic_floor_fine_planks_hybrid_source.svg').write_text(hybrid,encoding='utf-8')
    return floor


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--config',default='config.json'); ap.add_argument('--output',default='generated'); a=ap.parse_args()
    cp=Path(a.config).resolve(); root=cp.parent; out=(root/a.output).resolve() if not Path(a.output).is_absolute() else Path(a.output); out.mkdir(parents=True,exist_ok=True); cfg=load_config(cp)
    wall=build_wall(cfg,root,out); floor=build_floor(cfg,root,out)
    glass=build_svg(cfg); (out/'stained_glass_complex_vector_source.svg').write_text(glass,encoding='utf-8'); w=cfg['windows']; cairosvg.svg2pdf(bytestring=glass.encode(),write_to=str(out/'02_STAINED_GLASS_COMPLEX_TRANSLUCENT_280x330mm.pdf'),output_width=mm_to_pt(w['sheet_width_mm']),output_height=mm_to_pt(w['sheet_height_mm'])); cairosvg.svg2png(bytestring=glass.encode(),write_to=str(out/'stained_glass_complex_preview.png'),output_width=mm_to_px(w['sheet_width_mm'],cfg['dpi']),output_height=mm_to_px(w['sheet_height_mm'],cfg['dpi']))
    note=textwrap.dedent('''LUBA 3 AWD GOTHIC GARAGE\nPrint files 01, 02 and 03 at exactly 100%; never Fit to page.\nWall: opaque white exterior PVC + matte UV laminate.\nStained glass: translucent/backlit film, no opaque white underprint; install from inside.\nFloor: exterior PVC + matte UV laminate suitable for horizontal exposure.\nUse the print shop ICC profile and test color, adhesion and actual LED illumination.\n'''); (out/'README_FOR_PRINT_SHOP_RU_SI.txt').write_text(note,encoding='utf-8')
    wp=wall.resize((1800,int(1800*wall.height/wall.width))); fp=floor.resize((650,int(650*floor.height/floor.width))); prev=Image.new('RGB',(1880,wp.height+fp.height+110),'white'); prev.paste(wp,(40,35)); prev.paste(fp,(40,70+wp.height)); prev.save(out/'PREVIEW.jpg',quality=92)

if __name__=='__main__': main()
