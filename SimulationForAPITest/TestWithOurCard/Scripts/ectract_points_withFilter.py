import sumolib

# Charger le réseau SUMO
net = sumolib.net.readNet("H2ST.net.xml")

# Types de routes à garder pour TomTom
KEEP_TYPES = {
    "highway.primary",
    "highway.primary_link",
    "highway.secondary",
    "highway.secondary_link",
    "highway.tertiary",
    "highway.tertiary_link",
    "highway.trunk",
    "highway.trunk_link",
    "highway.residential",
    "highway.unclassified"
}

count = 0

with open("filtered_points_tomtom.txt", "w") as f:
    for edge in net.getEdges():
        if edge.getID().startswith(":"):  # exclure edges internes
            continue

        edge_type = edge.getType() or ""
        if edge_type not in KEEP_TYPES:
            continue  # ignorer bus, tram, pedestrian, service, etc.

        shape = edge.getShape()
        if not shape:
            continue

        mid_index = len(shape) // 2
        x_mid, y_mid = shape[mid_index]
        lon, lat = net.convertXY2LonLat(x_mid, y_mid)
        f.write(f"{edge.getID()},{lat},{lon}\n")
        count += 1

print(f"✅ {count} points créés et sauvegardés dans edges_points_tomtom.txt")
