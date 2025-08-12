import xml.etree.ElementTree as ET
import json
import os
import re

OSM_FILE = 'osm/H2ST_clean_fixed.osm'
OUTPUT_FILE = 'data/filtered_intersections_all_zones.json'

TARGET_NAMES = {
    "CFC", "Hay Hassani nord", "Hay hassani sud", "Oulfa", "Hay salam", "Lissasfa Nord"
}

def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name)

print("Loading OSM file...")
tree = ET.parse(OSM_FILE)
root = tree.getroot()

print("Extracting nodes...")
nodes = {}
for node in root.findall('node'):
    node_id = node.attrib['id']
    lat = float(node.attrib['lat'])
    lon = float(node.attrib['lon'])
    nodes[node_id] = (lat, lon)

print("Counting node occurrences in ways...")
node_way_count = {}
for way in root.findall('way'):
    nd_refs = [nd.attrib['ref'] for nd in way.findall('nd')]
    for nid in nd_refs:
        node_way_count[nid] = node_way_count.get(nid, 0) + 1

def extract_zone_nodes(zone_name):
    zone_node_ids = set()
    for way in root.findall('way'):
        name_tag = way.find("tag[@k='name']")
        if name_tag is not None and name_tag.attrib['v'] == zone_name:
            nd_refs = [nd.attrib['ref'] for nd in way.findall('nd')]
            zone_node_ids.update(nd_refs)
    for relation in root.findall('relation'):
        name_tag = relation.find("tag[@k='name']")
        if name_tag is not None and name_tag.attrib['v'] == zone_name:
            for member in relation.findall('member'):
                if member.attrib['type'] == 'way':
                    way_id = member.attrib['ref']
                    way = root.find(f"way[@id='{way_id}']")
                    if way is not None:
                        nd_refs = [nd.attrib['ref'] for nd in way.findall('nd')]
                        zone_node_ids.update(nd_refs)
                elif member.attrib['type'] == 'node':
                    zone_node_ids.add(member.attrib['ref'])
    return zone_node_ids

print("Processing zones and filtering intersection points...")

all_zones_data = []

for zone in TARGET_NAMES:
    print(f"Processing zone: {zone}")
    zone_node_ids = extract_zone_nodes(zone)
    intersection_nodes = [nid for nid in zone_node_ids if node_way_count.get(nid, 0) > 1 and nid in nodes]
    points = [{"lat": nodes[nid][0], "lon": nodes[nid][1]} for nid in intersection_nodes]

    all_zones_data.append({
        "zone": zone,
        "point_count": len(points),
        "points": points
    })

print(f"Saving all zones data to {OUTPUT_FILE}...")
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(all_zones_data, f, ensure_ascii=False, indent=2)

print("✅ Done.")
