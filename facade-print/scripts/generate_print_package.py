#!/usr/bin/env python3
from __future__ import annotations
import argparse, random, textwrap, math
from pathlib import Path
import cairosvg
import numpy as np
from PIL import Image, ImageDraw
from common import (load_config,load_asset,mm_to_px,mm_to_pt,pointed_path,pointed_mask,
                    entrance_geometry,entrance_mask,image_pdf,data_uri)
from textures import generate_wood_piece
from stained_glass import build_svg


def _segment_bounds_px(segments_mm,dpi):
    bounds=[0]; total=0.0
    for segment in segments_mm:
        total+=segment; bounds.append(mm_to_px(total,dpi))
    return bounds


def _restore_rear_seam_buttress(wall,cfg):
    """Split one complete realistic buttress across the rear-centre join."""
    dpi=cfg['dpi']; w=cfg['wall']; bounds=_segment_bounds_px(w['segments_mm'],dpi)
    wrap_end=bounds[-2]
    source_center=mm_to_px(w['rear_seam_buttress_source_center_mm'],dpi)
    half=max(1,mm_to_px(w['rear_seam_buttress_half_width_mm'],dpi))
    patch=wall.crop((source_center-half,0,source_center+half,wall.height))
    left=patch.crop((0,0,half,patch.height)); right=patch.crop((half,0,patch.width,patch.height))
    feather=min(half,max(1,mm_to_px(w.get('rear_seam_buttress_feather_mm',10),dpi)))

    left_alpha=np.full((wall.height,left.width),255,dtype=np.uint8)
    for x in range(feather):
        left_alpha[:,x]=round(255*x/max(1,feather-1))
    wall.paste(left,(wrap_end-left.width,0),Image.fromarray(left_alpha,'L'))

    right_alpha=np.full((wall.height,right.width),255,dtype=np.uint8)
    for i in range(feather):
        x=right.width-feather+i
        right_alpha[:,x]=round(255*(feather-1-i)/max(1,feather-1))
    wall.paste(right,(0,0),Image.fromarray(right_alpha,'L'))

    overlap=bounds[-1]-bounds[-2]
    if overlap>0:
        wall.paste(wall.crop((0,0,overlap,wall.height)),(wrap_end,0))
    return wall


def _save_wall_diagnostics(wall,cfg,out):
    dpi=cfg['dpi']; w=cfg['wall']; win=cfg['windows']; crops=[]
    for index,cx in enumerate(win['centers_x_mm'],1):
        left=mm_to_px(cx-120,dpi); right=mm_to_px(cx+120,dpi)
        top=mm_to_px(60,dpi); bottom=mm_to_px(450,dpi)
        crop=wall.crop((left,top,right,bottom)); crop.save(out/f'WINDOW_{index}_ALIGNMENT_DETAIL.jpg',quality=96,subsampling=0)
        crops.append(crop)
    bounds=_segment_bounds_px(w['segments_mm'],dpi); wrap_end=bounds[-2]; seam_width=mm_to_px(180,dpi)
    seam=Image.new('RGB',(seam_width*2,wall.height),'white')
    seam.paste(wall.crop((wrap_end-seam_width,0,wrap_end,wall.height)),(0,0))
    seam.paste(wall.crop((0,0,seam_width,wall.height)),(seam_width,0))
    seam.save(out/'REAR_SEAM_ASSEMBLED_DETAIL.jpg',quality=96,subsampling=0)
    gap=30; preview=Image.new('RGB',(sum(c.width for c in crops)+seam.width+gap*2,max([c.height for c in crops]+[seam.height])),'white')
    x=0
    for crop in crops:
        preview.paste(crop,(x,0)); x+=crop.width+gap
    preview.paste(seam,(x,0)); preview.thumbnail((2200,900),Image.Resampling.LANCZOS)
    preview.save(out/'WALL_ALIGNMENT_DIAGNOSTICS.jpg',quality=95,subsampling=0)


def build_wall(cfg,root,out):
    dpi=cfg['dpi']; w=cfg['wall']; win=cfg['windows']
    wall=load_asset(root/cfg['assets']['wall_base'])
    wall=wall.resize((mm_to_px(w['width_mm'],dpi),mm_to_px(w['height_mm'],dpi)),Image.Resampling.LANCZOS)
    wall=_restore_rear_seam_buttress(wall,cfg)
    for cx in win['centers_x_mm']:
        opening=pointed_mask(wall.size,cx,win['top_mm'],win['width_mm'],win['height_mm'],win['arch_height_mm'],dpi)
        wall.paste((255,255,255),(0,0),opening)
    wall.paste((255,255,255),(0,0),entrance_mask(wall.size,cfg,dpi))
    _save_wall_diagnostics(wall,cfg,out)
    art=out/'wall_stone_with_window_openings.png'; wall.save(art,optimize=True,dpi=(dpi,dpi))
    pdf=out/'01_WALLS_STONE_WINDOW_OPENINGS_3875x610mm_100pct.pdf'; image_pdf(art,pdf,w['width_mm'],w['height_mm'],'Luba garage wall film')
    ep,_=entrance_geometry(cfg); windows='\n'.join(f'<path d="{pointed_path(cx,win["top_mm"],win["width_mm"],win["height_mm"],win["arch_height_mm"])}"/>' for cx in win['centers_x_mm'])
    cuts=f'''<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="{w['width_mm']}mm" height="{w['height_mm']}mm" viewBox="0 0 {w['width_mm']} {w['height_mm']}"><g id="ENTRANCE_CUT" fill="none" stroke="#ff00ff" stroke-width=".25"><path d="{ep}"/></g><g id="WINDOW_CUTS" fill="none" stroke="#00a7ff" stroke-width=".25">{windows}</g></svg>'''
    (out/'01B_WALL_CUT_CONTOURS_3875x610mm.svg').write_text(cuts,encoding='utf-8')
    cairosvg.svg2pdf(bytestring=cuts.encode(),write_to=str(out/'01B_WALL_CUT_CONTOURS_3875x610mm.pdf'),output_width=mm_to_pt(w['width_mm']),output_height=mm_to_pt(w['height_mm']))
    bounds=[]; x=0
    for seg in w['segments_mm'][:-1]: x+=seg; bounds.append(x)
    guides=''.join(f'<line x1="{x}" y1="0" x2="{x}" y2="{w["height_mm"]}"/>' for x in bounds)
    hybrid=f'''<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w['width_mm']}mm" height="{w['height_mm']}mm" viewBox="0 0 {w['width_mm']} {w['height_mm']}"><g id="ARTWORK"><image width="{w['width_mm']}" height="{w['height_mm']}" preserveAspectRatio="none" xlink:href="data:image/png;base64,{data_uri(art)}"/></g><g id="ENTRANCE_CUT" style="display:none;fill:none;stroke:#ff00ff;stroke-width:.25"><path d="{ep}"/></g><g id="WINDOW_CUTS" style="display:none;fill:none;stroke:#00a7ff;stroke-width:.25">{windows}</g><g id="PANEL_GUIDES" style="display:none;fill:none;stroke:#777;stroke-width:.18;stroke-dasharray:3,2">{guides}<line x1="0" y1="{w['top_fold_mm']}" x2="{w['width_mm']}" y2="{w['top_fold_mm']}"/></g></svg>'''
    (out/'wall_wrap_hybrid_with_cut_layers.svg').write_text(hybrid,encoding='utf-8')
    return wall


def _plank_widths(total,minimum,maximum,rng):
    n=max(math.ceil(total/maximum),min(math.floor(total/minimum),round(total/((minimum+maximum)/2))))
    base=total/n; raw=[rng.uniform(-1,1) for _ in range(n)]; mean=sum(raw)/n; raw=[v-mean for v in raw]
    max_abs=max(abs(v) for v in raw) or 1; amplitude=.9*min(base-minimum,maximum-base)
    return [base+v/max_abs*amplitude for v in raw]


def _floor_breaks(height,minimum,maximum,clearance,previous,rng):
    n_min=math.ceil(height/maximum); n_max=math.floor(height/minimum)
    candidates=[]
    for _ in range(80):
        count=rng.randint(n_min,n_max); remaining=height; lengths=[]
        for index in range(count-1):
            left=count-index-1
            low=max(minimum,remaining-maximum*left); high=min(maximum,remaining-minimum*left)
            length=rng.uniform(low,high); lengths.append(length); remaining-=length
        lengths.append(remaining); breaks=[]; acc=0
        for length in lengths[:-1]: acc+=length; breaks.append(acc)
        distance=min((abs(a-b) for a in breaks for b in previous),default=height)
        candidates.append((distance,breaks))
        if distance>=clearance: return breaks
    return max(candidates,key=lambda item:item[0])[1]


def build_floor(cfg,root,out):
    f=cfg['floor']; dpi=f.get('dpi',cfg['dpi']); rng=random.Random(cfg['random_seed'])
    size=(mm_to_px(f['file_width_mm'],dpi),mm_to_px(f['file_height_mm'],dpi)); floor=Image.new('RGB',size,(58,37,25)); d=ImageDraw.Draw(floor,'RGBA')
    widths=_plank_widths(f['trim_width_mm'],f['plank_width_min_mm'],f['plank_width_max_mm'],rng)
    top=f['trim_offset_y_mm']; bottom=top+f['trim_height_mm']; xmm=f['trim_offset_x_mm']; previous=[]
    for i,pw in enumerate(widths):
        breaks=_floor_breaks(f['trim_height_mm'],f.get('plank_length_min_mm',180),f.get('plank_length_max_mm',360),f.get('joint_clearance_mm',45),previous,rng)
        positions=[0.0]+breaks+[f['trim_height_mm']]; x0=mm_to_px(xmm,dpi); x1=mm_to_px(xmm+pw,dpi)
        for j,(a,b) in enumerate(zip(positions,positions[1:])):
            y0=mm_to_px(top+a,dpi); y1=mm_to_px(top+b,dpi)
            piece=generate_wood_piece(max(2,x1-x0),max(2,y1-y0),cfg['random_seed']+10000+i*101+j*17,dpi)
            floor.paste(piece,(x0,y0))
            if j>0:
                d.line([(x0+1,y0),(x1-1,y0)],fill=(27,18,13,235),width=max(1,mm_to_px(.8,dpi)))
                for nx in (x0+max(2,mm_to_px(2.3,dpi)),x1-max(2,mm_to_px(2.3,dpi))):
                    r=max(1,mm_to_px(.65,dpi)); d.ellipse([nx-r,y0-r,nx+r,y0+r],fill=(30,28,26,220))
        d.line([(x0,mm_to_px(top,dpi)),(x0,mm_to_px(bottom,dpi))],fill=(26,18,13,230),width=max(1,mm_to_px(.75,dpi)))
        previous=breaks; xmm+=pw
    art=out/'attic_floor_fine_planks.jpg'; floor.save(art,quality=95,subsampling=0,dpi=(dpi,dpi))
    image_pdf(art,out/'03_ATTIC_FLOOR_FINE_PLANKS_1004x931mm_100pct.pdf',f['file_width_mm'],f['file_height_mm'],'Luba garage attic floor')
    hybrid=f'''<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{f['file_width_mm']}mm" height="{f['file_height_mm']}mm" viewBox="0 0 {f['file_width_mm']} {f['file_height_mm']}"><image width="{f['file_width_mm']}" height="{f['file_height_mm']}" preserveAspectRatio="none" xlink:href="data:image/jpeg;base64,{data_uri(art)}"/><g id="TRIM_CONTOUR" style="display:none;fill:none;stroke:#ff00ff;stroke-width:.25"><rect x="{f['trim_offset_x_mm']}" y="{f['trim_offset_y_mm']}" width="{f['trim_width_mm']}" height="{f['trim_height_mm']}"/></g></svg>'''; (out/'attic_floor_fine_planks_hybrid_source.svg').write_text(hybrid,encoding='utf-8')
    crop_mm=250; crop_px=mm_to_px(crop_mm,dpi); cx=mm_to_px(f['trim_offset_x_mm']+f['trim_width_mm']/2,dpi); cy=mm_to_px(f['trim_offset_y_mm']+f['trim_height_mm']/2,dpi)
    detail=floor.crop((cx-crop_px//2,cy-crop_px//2,cx+crop_px//2,cy+crop_px//2)); detail.save(out/'FLOOR_DETAIL_250x250mm_PREVIEW.jpg',quality=95,subsampling=0,dpi=(dpi,dpi))
    return floor


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--config',default='config.json'); ap.add_argument('--output',default='generated'); a=ap.parse_args()
    cp=Path(a.config).resolve(); root=cp.parent; out=(root/a.output).resolve() if not Path(a.output).is_absolute() else Path(a.output); out.mkdir(parents=True,exist_ok=True); cfg=load_config(cp)
    wall=build_wall(cfg,root,out); floor=build_floor(cfg,root,out)
    glass=build_svg(cfg); (out/'stained_glass_complex_vector_source.svg').write_text(glass,encoding='utf-8'); w=cfg['windows']; cairosvg.svg2pdf(bytestring=glass.encode(),write_to=str(out/'02_STAINED_GLASS_COMPLEX_TRANSLUCENT_280x330mm.pdf'),output_width=mm_to_pt(w['sheet_width_mm']),output_height=mm_to_pt(w['sheet_height_mm'])); cairosvg.svg2png(bytestring=glass.encode(),write_to=str(out/'stained_glass_complex_preview.png'),output_width=mm_to_px(w['sheet_width_mm'],cfg['dpi']),output_height=mm_to_px(w['sheet_height_mm'],cfg['dpi']))
    note=textwrap.dedent('''LUBA 3 AWD GOTHIC GARAGE\nPrint files 01, 02 and 03 at exactly 100%; never Fit to page.\nWall: opaque white exterior PVC + matte UV laminate.\nStained glass: translucent/backlit film, no opaque white underprint; install from inside.\nFloor: exterior PVC + matte UV laminate suitable for horizontal exposure.\nUse the print shop ICC profile and test color, adhesion and actual LED illumination.\n'''); (out/'README_FOR_PRINT_SHOP_RU_SI.txt').write_text(note,encoding='utf-8')
    wp=wall.resize((1800,int(1800*wall.height/wall.width))); fp=floor.resize((1200,int(1200*floor.height/floor.width))); prev=Image.new('RGB',(1880,wp.height+fp.height+110),'white'); prev.paste(wp,(40,35)); prev.paste(fp,(40,70+wp.height)); prev.save(out/'PREVIEW.jpg',quality=92)


if __name__=='__main__': main()
