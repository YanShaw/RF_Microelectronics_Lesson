"""Generate original L001 band-location diagram and verify lesson arithmetic.

This is a diagram builder and arithmetic check, not a transistor simulation.
Dependencies: Pillow. All signal voltages in example A are peak values.
"""
from pathlib import Path
from html import escape
import json
import math
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
W, H = 1200, 800
im = Image.new('RGB', (W, H), '#f8fafc')
draw = ImageDraw.Draw(im)
FONT = Path('C:/Windows/Fonts/msyh.ttc')
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       '<rect width="100%" height="100%" fill="#f8fafc"/>']

def label(x, y, text, size=24, fill='#172b4d'):
    font = ImageFont.truetype(str(FONT), size)
    draw.text((x, y), text, font=font, fill=fill)
    svg.append(f'<text x="{x}" y="{y+size}" font-family="Microsoft YaHei, sans-serif" font-size="{size}" fill="{fill}">{escape(text)}</text>')

def line(x1, y1, x2, y2, color='#65758b', width=2):
    draw.line((x1,y1,x2,y2), fill=color, width=width)
    svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>')

def rect(x1, y1, x2, y2, fill, stroke):
    draw.rectangle((x1,y1,x2,y2), fill=fill, outline=stroke, width=2)
    svg.append(f'<rect x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')

label(54, 24, '同一段信息，搬到不同的中心频率', 34)
label(54, 80, '理想实数混频：RF 2450 MHz × LO 2440 MHz', 25)
bands = [
    ('RF 输入', 2450, 2449, 2451, '#dbeafe', '#2563eb'),
    ('差频输出 · 保留', 10, 9, 11, '#ccfbf1', '#0f766e'),
    ('和频输出 · 滤除', 4890, 4889, 4891, '#e2e8f0', '#64748b'),
]
for i,(title,fc,lo,hi,fill,color) in enumerate(bands):
    y = 245 + i*185
    label(54, y-105, title, 24, color)
    label(54, y-65, f'中心 {fc} MHz', 21)
    x1, x2 = 330, 1110
    def xpos(freq):
        return x1+(freq-(fc-2))/4*(x2-x1)
    rect(xpos(lo),y-70,xpos(hi),y,fill,color)
    label(630, y-53, '带宽 2 MHz', 23, color)
    line(x1,y,x2,y)
    for offset in range(-2,3):
        x=xpos(fc+offset)
        line(x,y,x,y+9)
        label(x-29,y+16,str(fc+offset),20)
    label(1060,y+48,'MHz',19)
label(54, 718, '只画正频率；各行使用局部频率轴。矩形表示占用范围，不表示真实谱形。', 21)
label(54, 753, '三行高度不比较幅度；理想单位余弦相乘的和频、差频电压系数均为 1/2。', 21)
svg.append('</svg>')
(OUT/'frequency_translation.svg').write_text('\n'.join(svg),encoding='utf-8')
im.save(OUT/'frequency_translation.png')

result = {
    'model': 'ideal normalized real multiplier; no loading; example A peak voltage',
    'rf_Hz': 2.45e9, 'lo_Hz': 2.44e9,
    'difference_Hz': 2.45e9-2.44e9, 'sum_Hz': 2.45e9+2.44e9,
    'rf_edges_Hz': [2.449e9,2.451e9],
    'if_edges_Hz': [2.449e9-2.44e9,2.451e9-2.44e9],
    'sum_edges_Hz': [2.449e9+2.44e9,2.451e9+2.44e9],
    'voltage_peaks_V': [0.2e-3,0.2e-3*10,0.2e-3*10/2,0.2e-3*10/2*5],
    'image_Hz': 2.44e9-10e6,
    'one_pF_Xc_at_2p45GHz_ohm': 1/(2*math.pi*2.45e9*1e-12),
    'one_pF_Xc_at_10MHz_ohm': 1/(2*math.pi*10e6*1e-12),
    'noise_example_without_LNA_uV_RMS': math.sqrt(1**2+10**2),
    'noise_example_with_LNA_uV_RMS': math.sqrt((10*1)**2+(10*1)**2+10**2),
    'snr_without_LNA_linear': 10**2/(1**2+10**2),
    'snr_with_LNA_linear': (10*10)**2/((10*1)**2+(10*1)**2+10**2),
    'exercise_highside_if_Hz': abs(2.45e9-2.46e9),
    'exercise_highside_image_Hz': 2.46e9+10e6,
    'exercise_changed_lo_if_Hz': 2.45e9-2.439e9,
    'exercise_changed_lo_edges_Hz': [2.449e9-2.439e9,2.451e9-2.439e9],
}
assert result['difference_Hz']==10e6 and result['sum_Hz']==4.89e9
assert result['if_edges_Hz']==[9e6,11e6]
assert result['voltage_peaks_V'][-1]==0.005
assert result['exercise_highside_image_Hz']==2.47e9
assert result['exercise_changed_lo_edges_Hz']==[10e6,12e6]
assert result['snr_with_LNA_linear'] < (10/1)**2
(OUT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=True,indent=2))
