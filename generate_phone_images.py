"""
generate_phone_images.py
========================
Generates clean SVG phone placeholder images locally (no internet needed).
Each image shows the iPhone model name on a realistic dark phone silhouette.

Run:  python generate_phone_images.py
"""

import os, sys, django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_system.settings')
django.setup()

ITEM_DIR  = BASE_DIR / 'media' / 'inventory' / 'items'
ASSET_DIR = BASE_DIR / 'media' / 'assets' / 'images'
ITEM_DIR.mkdir(parents=True, exist_ok=True)
ASSET_DIR.mkdir(parents=True, exist_ok=True)

# ── SVG template — realistic dark phone silhouette ─────────────────────────────
def make_phone_svg(model_line1: str, model_line2: str, color: str = '#1C1C1E') -> str:
    """
    Generates a clean SVG that looks like a modern smartphone.
    model_line1 = e.g. "iPhone 16 Pro"
    model_line2 = e.g. "256 GB"
    color       = body color hex
    """
    # Slightly different accent colors per generation
    accent = {
        '12': '#4A90D9', '13': '#5B5EA6', '14': '#2D6A4F',
        '14p': '#6B3FA0', '15': '#E07A5F', '15p': '#2C3E50',
        '15pm': '#2C3E50', '16': '#264653', '16p': '#1A1A2E',
        '16pm': '#1A1A2E', '17': '#0F3460', '17p': '#16213E',
        '17pm': '#16213E',
    }.get(''.join(filter(str.isalnum, model_line1.lower().replace('iphone','').replace(' ','').replace('(','').replace(')','').replace('gb','').strip()))[:4], '#1C1C1E')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 580" width="300" height="580">
  <defs>
    <linearGradient id="body" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%"   stop-color="{color}" stop-opacity="1"/>
      <stop offset="100%" stop-color="#0a0a0a" stop-opacity="1"/>
    </linearGradient>
    <linearGradient id="screen" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="#1a1a2e"/>
      <stop offset="100%" stop-color="#16213e"/>
    </linearGradient>
    <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"   stop-color="#ffffff" stop-opacity="0.15"/>
      <stop offset="50%"  stop-color="#ffffff" stop-opacity="0.03"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
    <filter id="shadow">
      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#000" flood-opacity="0.5"/>
    </filter>
  </defs>

  <!-- Phone body -->
  <rect x="20" y="10" width="260" height="560" rx="40" ry="40"
        fill="url(#body)" filter="url(#shadow)"/>

  <!-- Side shine -->
  <rect x="20" y="10" width="260" height="560" rx="40" ry="40"
        fill="url(#shine)"/>

  <!-- Screen bezel -->
  <rect x="30" y="55" width="240" height="470" rx="20" ry="20"
        fill="#0a0a0c"/>

  <!-- Screen -->
  <rect x="34" y="59" width="232" height="462" rx="18" ry="18"
        fill="url(#screen)"/>

  <!-- Dynamic Island (iPhone 14 Pro+) or notch -->
  <rect x="108" y="68" width="84" height="28" rx="14" ry="14"
        fill="#0a0a0a"/>

  <!-- Camera system (top-right cluster) -->
  <g transform="translate(195,95)">
    <!-- Camera bump background -->
    <rect x="-38" y="-38" width="76" height="76" rx="18"
          fill="#111" stroke="#2a2a2a" stroke-width="1.5"/>
    <!-- Main lens -->
    <circle cx="0" cy="-10" r="18" fill="#0a0a0a" stroke="#333" stroke-width="1"/>
    <circle cx="0" cy="-10" r="13" fill="#1a1a1a"/>
    <circle cx="0" cy="-10" r="7"  fill="#0d0d0d"/>
    <circle cx="-4" cy="-14" r="2" fill="#444" opacity="0.8"/>
    <!-- Ultra-wide lens -->
    <circle cx="-18" cy="14" r="13" fill="#0a0a0a" stroke="#333" stroke-width="1"/>
    <circle cx="-18" cy="14" r="8"  fill="#1a1a1a"/>
    <circle cx="-18" cy="14" r="4"  fill="#0d0d0d"/>
    <!-- Tele lens -->
    <circle cx="18"  cy="14" r="13" fill="#0a0a0a" stroke="#333" stroke-width="1"/>
    <circle cx="18"  cy="14" r="8"  fill="#1a1a1a"/>
    <circle cx="18"  cy="14" r="4"  fill="#0d0d0d"/>
    <!-- Flash -->
    <circle cx="18" cy="-24" r="6" fill="#554422" stroke="#665533" stroke-width="1"/>
    <circle cx="18" cy="-24" r="3" fill="#ffe08a" opacity="0.6"/>
  </g>

  <!-- Screen content — Apple logo -->
  <text x="150" y="280" font-family="Arial,Helvetica,sans-serif"
        font-size="52" text-anchor="middle" fill="#ffffff" opacity="0.18"></text>

  <!-- Model name on screen -->
  <text x="150" y="340" font-family="-apple-system,BlinkMacSystemFont,Arial,sans-serif"
        font-size="22" font-weight="600" text-anchor="middle"
        fill="#ffffff" opacity="0.85">{model_line1}</text>
  <text x="150" y="368" font-family="-apple-system,BlinkMacSystemFont,Arial,sans-serif"
        font-size="15" font-weight="400" text-anchor="middle"
        fill="#8e8e93" opacity="0.9">{model_line2}</text>

  <!-- Home indicator bar -->
  <rect x="105" y="500" width="90" height="5" rx="2.5"
        fill="#ffffff" opacity="0.25"/>

  <!-- Side buttons -->
  <rect x="15" y="120" width="5" height="50" rx="2.5" fill="#2a2a2a"/>
  <rect x="15" y="185" width="5" height="70" rx="2.5" fill="#2a2a2a"/>
  <rect x="280" y="140" width="5" height="80" rx="2.5" fill="#2a2a2a"/>
</svg>'''


# ── Phone definitions ───────────────────────────────────────────────────────────
PHONES = [
    ('iphone12',    'iPhone 12',        '128GB / 256GB',  '#1C1C1E'),
    ('iphone13',    'iPhone 13',        '128GB / 256GB',  '#1D1D1F'),
    ('iphone14',    'iPhone 14',        '128GB / 256GB',  '#2C2C2E'),
    ('iphone14pro', 'iPhone 14 Pro',    '256GB',          '#2C2C2E'),
    ('iphone15',    'iPhone 15',        '128GB / 256GB',  '#1C1C1E'),
    ('iphone15pro', 'iPhone 15 Pro',    '256GB / 512GB',  '#1A1A1A'),
    ('iphone16',    'iPhone 16',        '128GB / 256GB',  '#1C1C1E'),
    ('iphone16pro', 'iPhone 16 Pro',    '256GB / 512GB',  '#16161A'),
    ('iphone17',    'iPhone 17',        '256GB / 512GB',  '#1C1C1E'),
    ('iphone17pro', 'iPhone 17 Pro',    '256GB / 512GB',  '#12121A'),
]

print('=== Generating iPhone SVG images ===')
for key, line1, line2, color in PHONES:
    svg = make_phone_svg(line1, line2, color)
    fname = f'{key}.svg'

    item_path  = ITEM_DIR  / fname
    asset_path = ASSET_DIR / fname

    item_path.write_text(svg,  encoding='utf-8')
    asset_path.write_text(svg, encoding='utf-8')
    print(f'  ✔ Generated: {fname}')

print(f'\n=== Updating database ===')

from apps.inventory.models import InventoryItem
from apps.assets.models import Asset

def get_key(name):
    n = name.lower()
    if 'iphone 17 pro' in n:  return 'iphone17pro'
    if 'iphone 17'     in n:  return 'iphone17'
    if 'iphone 16 pro' in n:  return 'iphone16pro'
    if 'iphone 16'     in n:  return 'iphone16'
    if 'iphone 15 pro' in n:  return 'iphone15pro'
    if 'iphone 15'     in n:  return 'iphone15'
    if 'iphone 14 pro' in n:  return 'iphone14pro'
    if 'iphone 14'     in n:  return 'iphone14'
    if 'iphone 13'     in n:  return 'iphone13'
    if 'iphone 12'     in n:  return 'iphone12'
    return None

ic = ac = 0
for item in InventoryItem.objects.filter(category__category_name='Mobile Phones'):
    k = get_key(item.item_name)
    if k:
        item.image     = f'inventory/items/{k}.svg'
        item.image_url = ''
        item.save(update_fields=['image', 'image_url'])
        ic += 1
        print(f'  ✔ Item: {item.item_name}')

for asset in Asset.objects.filter(category__category_name='Mobile Devices'):
    k = get_key(asset.asset_name)
    if k:
        asset.image     = f'assets/images/{k}.svg'
        asset.image_url = ''
        asset.save(update_fields=['image', 'image_url'])
        ac += 1

print(f'\n✅ Done: {ic} inventory items + {ac} assets now have local SVG images.')
