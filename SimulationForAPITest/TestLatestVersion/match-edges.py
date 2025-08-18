import json
import sumolib
import math

# Fichiers
CLEAN_JSON = "tomtom_clean_with_edges.json"
SUMO_NET = "H2ST8.net.xml"
OUTPUT_JSON = "tomtom_matched_edges.json"

# Charger le réseau SUMO
net = sumolib.net.readNet(SUMO_NET)

# Charger les segments TomTom
with open(CLEAN_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

segments = data["segments"]

# Fonction pour calculer distance entre points
def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

# Fonction pour trouver l’edge SUMO le plus proche
def find_nearest_edge(lat, lon):
    try:
        x, y = net.convertLonLat2XY(lon, lat)
    except Exception as e:
        print(f"Erreur conversion LonLat: {lat}, {lon} → {e}")
        return None

    min_dist = float("inf")
    nearest_edge = None
    for edge in net.getEdges():
        for ex, ey in edge.getShape():
            d = distance(x, y, ex, ey)
            if d < min_dist:
                min_dist = d
                nearest_edge = edge
    return nearest_edge.getID() if nearest_edge else None

# Assigner edgeId à chaque segment
for seg in segments:
    if not seg["shape"]:
        seg["edgeId"] = None
        continue
    mid_index = len(seg["shape"]) // 2
    lat, lon = seg["shape"][mid_index]
    edge_id = find_nearest_edge(lat, lon)
    seg["edgeId"] = edge_id

# Sauvegarder le JSON avec edgeId
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump({"segments": segments}, f, indent=2, ensure_ascii=False)

print(f"✅ Matching terminé. JSON sauvegardé: {OUTPUT_JSON}")
