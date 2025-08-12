import xml.etree.ElementTree as ET
import json
import re
import os

OSM_FILE = 'osm/H2ST_clean_fixed.osm'
OUTPUT_DIR = 'sous_zones_json'

TARGET_NAMES = {
    "CFC", "Hay Hassani nord", "Hay hassani sud", "Oulfa", "Hay salam", "Lissasfa Nord"
}

def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name)

def compute_bbox(coords):
    lats = [lat for lat, lon in coords]
    lons = [lon for lat, lon in coords]
    return min(lats), min(lons), max(lats), max(lons)

print("Chargement du fichier OSM...")
tree = ET.parse(OSM_FILE)
root = tree.getroot()

print("Extraction des noeuds...")
nodes = {}
for node in root.findall('node'):
    node_id = node.attrib['id']
    lat = float(node.attrib['lat'])
    lon = float(node.attrib['lon'])
    nodes[node_id] = (lat, lon)

zones = {}

def extract_from_way(way, name):
    coords = []
    for nd in way.findall('nd'):
        nid = nd.attrib['ref']
        if nid in nodes:
            coords.append(nodes[nid])
    if coords:
        bbox = compute_bbox(coords)
        zones[name] = {"coords": coords, "bbox": bbox}

def extract_from_relation(relation, name):
    coords = []
    for member in relation.findall('member'):
        if member.attrib['type'] == 'node':
            nid = member.attrib['ref']
            if nid in nodes:
                coords.append(nodes[nid])
        elif member.attrib['type'] == 'way':
            way_id = member.attrib['ref']
            way = root.find(f"way[@id='{way_id}']")
            if way is not None:
                for nd in way.findall('nd'):
                    nid = nd.attrib['ref']
                    if nid in nodes:
                        coords.append(nodes[nid])
    if coords:
        bbox = compute_bbox(coords)
        zones[name] = {"coords": coords, "bbox": bbox}

print("Recherche dans <way>...")
for way in root.findall('way'):
    name_tag = way.find("tag[@k='name']")
    if name_tag is not None and name_tag.attrib['v'] in TARGET_NAMES:
        extract_from_way(way, name_tag.attrib['v'])

print("Recherche dans <relation>...")
for relation in root.findall('relation'):
    name_tag = relation.find("tag[@k='name']")
    if name_tag is not None and name_tag.attrib['v'] in TARGET_NAMES:
        extract_from_relation(relation, name_tag.attrib['v'])

os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"Sauvegarde des données dans '{OUTPUT_DIR}'...")
for name, data in zones.items():
    sanitized_name = sanitize_filename(name)
    output_path = os.path.join(OUTPUT_DIR, f"{sanitized_name}.json")
    json_data = {
        "name": name,
        "point_count": len(data["coords"]),  # ✅ ajout du nombre de points
        "bbox": {
            "lat_min": data["bbox"][0],
            "lon_min": data["bbox"][1],
            "lat_max": data["bbox"][2],
            "lon_max": data["bbox"][3]
        },
        "points": [{"lat": lat, "lon": lon} for lat, lon in data["coords"]]
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"Zone: {name} - Points: {len(data['coords'])}")  # ✅ affichage console

print(f"{len(zones)} fichiers JSON créés.")
