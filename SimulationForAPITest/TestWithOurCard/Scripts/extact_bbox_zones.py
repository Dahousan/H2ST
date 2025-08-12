import xml.etree.ElementTree as ET
import json
import re
import os

OSM_FILE = "osm/H2ST_clean_fixed.osm" 
OUTPUT_FILE = "data/zones_bbox.json"

TARGET_NAMES = {
    "CFC", "Hay Hassani nord", "Hay hassani sud", "Oulfa", "Hay salam", "Lissasfa Nord"
}

def sanitize_name(name):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name)

def compute_bbox(coords):
    lats = [lat for lat, lon in coords]
    lons = [lon for lat, lon in coords]
    return min(lons), min(lats), max(lons), max(lats)  # (minLon, minLat, maxLon, maxLat)

print("Chargement du fichier OSM...")
tree = ET.parse(OSM_FILE)
root = tree.getroot()

print("Extraction des noeuds...")
nodes = {}
for node in root.findall('node'):
    nid = node.get('id')
    lat = float(node.get('lat'))
    lon = float(node.get('lon'))
    nodes[nid] = (lat, lon)

zones = {}

def extract_points_from_way(way):
    coords = []
    for nd in way.findall('nd'):
        nid = nd.get('ref')
        if nid in nodes:
            coords.append(nodes[nid])
    return coords

def extract_points_from_relation(relation):
    coords = []
    for member in relation.findall('member'):
        if member.get('type') == 'node':
            nid = member.get('ref')
            if nid in nodes:
                coords.append(nodes[nid])
        elif member.get('type') == 'way':
            way_id = member.get('ref')
            way = root.find(f"way[@id='{way_id}']")
            if way is not None:
                coords.extend(extract_points_from_way(way))
    return coords

print("Recherche des zones...")

for way in root.findall('way'):
    name_tag = way.find("tag[@k='name']")
    if name_tag is not None and name_tag.get('v') in TARGET_NAMES:
        coords = extract_points_from_way(way)
        if coords:
            bbox = compute_bbox(coords)
            zones[name_tag.get('v')] = bbox

for relation in root.findall('relation'):
    name_tag = relation.find("tag[@k='name']")
    if name_tag is not None and name_tag.get('v') in TARGET_NAMES:
        coords = extract_points_from_relation(relation)
        if coords:
            bbox = compute_bbox(coords)
            zones[name_tag.get('v')] = bbox

print(f"{len(zones)} zones trouvées. Sauvegarde dans {OUTPUT_FILE}...")

output_data = []
for name, bbox in zones.items():
    output_data.append({
        "zone": name,
        "bbox": {
            "minLon": bbox[0],
            "minLat": bbox[1],
            "maxLon": bbox[2],
            "maxLat": bbox[3]
        }
    })

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print("Terminé.")
