from __future__ import annotations
import math
from common import pointed_path

COLORS=['#c32c4c','#efaa27','#169070','#276bc2','#7d3cb2','#14a0b0']
LEAD='#171515'


def _tree(cx,top,bottom,left,right):
    p=[]; rows,cols=11,5; inner_l,inner_r=left+8,right-8
    cw=(inner_r-inner_l)/cols; ch=(bottom-top)/rows
    for r in range(rows):
        for c in range(cols):
            p.append(f'<rect x="{inner_l+c*cw:.2f}" y="{top+r*ch:.2f}" width="{cw+.3:.2f}" height="{ch+.3:.2f}" fill="{COLORS[(r*3+c)%6]}" stroke="{LEAD}" stroke-width=".8"/>')
    sy=top+43
    p += [f'<circle cx="{cx}" cy="{sy}" r="28" fill="#f2c242" stroke="{LEAD}" stroke-width="3"/>',
          f'<circle cx="{cx}" cy="{sy}" r="12" fill="#2c70c4" stroke="{LEAD}" stroke-width="2"/>']
    for a in range(0,360,30):
        x=cx+math.cos(math.radians(a))*27; y=sy+math.sin(math.radians(a))*27
        p.append(f'<line x1="{cx}" y1="{sy}" x2="{x:.2f}" y2="{y:.2f}" stroke="{LEAD}" stroke-width="1.4"/>')
    p.append(f'<path d="M {cx-6},{bottom} C {cx-7},{bottom-72} {cx-5},{bottom-154} {cx},{top+77} C {cx+5},{bottom-154} {cx+7},{bottom-72} {cx+6},{bottom} Z" fill="#8d522a" stroke="{LEAD}" stroke-width="2.2"/>')
    for yy,spread in [(bottom-60,30),(bottom-98,34),(bottom-138,32),(bottom-176,28),(bottom-210,22)]:
        for side in (-1,1):
            p.append(f'<path d="M {cx},{yy} C {cx+side*spread*.35},{yy-10} {cx+side*spread*.72},{yy-20} {cx+side*spread},{yy-33}" fill="none" stroke="{LEAD}" stroke-width="2"/>')
    leaves=['#16a16e','#d9b52a','#c93457','#2b75c7','#8c42b8','#19a4b1']
    for i in range(38):
        a=(i*137.5)%360; lx=cx+math.cos(math.radians(a))*(13+(i%5)*7); ly=top+92+(i%10)*18
        p.append(f'<ellipse cx="{lx:.2f}" cy="{ly:.2f}" rx="5" ry="8.4" transform="rotate({a:.2f} {lx:.2f} {ly:.2f})" fill="{leaves[i%6]}" stroke="{LEAD}" stroke-width="1.25"/>')
    return p


def _rose(cx,top,bottom,left,right):
    p=[]; ry=top+48
    p.append(f'<circle cx="{cx}" cy="{ry}" r="33" fill="#173a70" stroke="{LEAD}" stroke-width="3"/>')
    for ring,radius,petals in [(0,12,8),(1,23,12)]:
        for i in range(petals):
            a=360*i/petals; x=cx+math.cos(math.radians(a))*radius; y=ry+math.sin(math.radians(a))*radius
            p.append(f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="{5.2+ring}" ry="{10.5+ring*1.4}" transform="rotate({a+90:.2f} {x:.2f} {y:.2f})" fill="{COLORS[(i+ring*2)%6]}" stroke="{LEAD}" stroke-width="1.2"/>')
    p.append(f'<circle cx="{cx}" cy="{ry}" r="7.5" fill="#f3c64b" stroke="{LEAD}" stroke-width="1.7"/>')
    lower=top+86; h=bottom-lower
    for r in range(9):
        y0=lower+h*r/9; y1=lower+h*(r+1)/9; mid=cx+(8 if r%2 else -8)
        p.append(f'<path d="M {left+8},{y0} L {mid},{y0+6} L {right-8},{y0} L {right-8},{y1} L {cx},{y1-5} L {left+8},{y1} Z" fill="{COLORS[(r+1)%6]}" stroke="{LEAD}" stroke-width="1.2"/>')
    fy=lower+h*.5
    p.append(f'<path d="M {cx},{fy-48} C {cx-13},{fy-31} {cx-17},{fy-14} {cx-7},{fy-2} C {cx-23},{fy-12} {cx-34},{fy+2} {cx-27},{fy+20} C {cx-14},{fy+11} {cx-8},{fy+18} {cx-6},{fy+35} L {cx-17},{fy+35} L {cx-17},{fy+46} L {cx+17},{fy+46} L {cx+17},{fy+35} L {cx+6},{fy+35} C {cx+8},{fy+18} {cx+14},{fy+11} {cx+27},{fy+20} C {cx+34},{fy+2} {cx+23},{fy-12} {cx+7},{fy-2} C {cx+17},{fy-14} {cx+13},{fy-31} {cx},{fy-48} Z" fill="#f1c74b" stroke="{LEAD}" stroke-width="2.2"/>')
    return p


def window_group(group_id,x,y,w,h,arch,bleed,design):
    cx=x+(w+2*bleed)/2; top=y+bleed; bottom=top+h; left=cx-w/2; right=cx+w/2
    shape=pointed_path(cx,top,w,h,arch); clip='clip_'+group_id
    p=[f'<clipPath id="{clip}"><path d="{shape}"/></clipPath>',f'<g id="{group_id}" clip-path="url(#{clip})">',f'<rect x="{left}" y="{top}" width="{w}" height="{h}" fill="#143b73"/>']
    yy=top; i=0
    while yy<bottom:
        hh=min(16,bottom-yy)
        p += [f'<rect x="{left}" y="{yy}" width="8" height="{hh}" fill="{COLORS[i%6]}" stroke="{LEAD}" stroke-width="1"/>',f'<rect x="{right-8}" y="{yy}" width="8" height="{hh}" fill="{COLORS[(i+3)%6]}" stroke="{LEAD}" stroke-width="1"/>']
        yy+=16; i+=1
    p += _tree(cx,top,bottom,left,right) if design=='tree' else _rose(cx,top,bottom,left,right)
    for frac in (.25,.47,.69,.86):
        yy=top+h*frac; p.append(f'<line x1="{left}" y1="{yy}" x2="{right}" y2="{yy}" stroke="{LEAD}" stroke-width="1.25"/>')
    p += ['</g>',f'<path d="{shape}" fill="none" stroke="#151313" stroke-width="3.6"/>']
    return '\n'.join(p)


def build_svg(cfg: dict) -> str:
    w=cfg['windows']; sw,sh=w['sheet_width_mm'],w['sheet_height_mm']; pw=w['width_mm']+2*w['mounting_bleed_mm']; ph=w['height_mm']+2*w['mounting_bleed_mm']
    x1=16; x2=sw-16-pw; y=7
    return f'''<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="{sw}mm" height="{sh}mm" viewBox="0 0 {sw} {sh}">\n<title>Complex stained-glass inserts</title>\n{window_group('LEFT_TREE_OF_LIFE',x1,y,w['width_mm'],w['height_mm'],w['arch_height_mm'],w['mounting_bleed_mm'],'tree')}\n{window_group('RIGHT_ROSE_FLEUR_DE_LIS',x2,y,w['width_mm'],w['height_mm'],w['arch_height_mm'],w['mounting_bleed_mm'],'rose')}\n<g id="CUT_GUIDES" style="display:none;fill:none;stroke:#ff00ff;stroke-width:.25"><rect x="{x1}" y="{y}" width="{pw}" height="{ph}"/><rect x="{x2}" y="{y}" width="{pw}" height="{ph}"/></g>\n</svg>'''
