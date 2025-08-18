import sumolib

# Charger le réseau SUMO
net = sumolib.net.readNet("H2ST8.net.xml")

count = 0  # compteur

with open("edges_points_tomtom.txt", "w") as f:
    for edge in net.getEdges():
        if edge.getID().startswith(":"):  # exclure edges internes
            continue

        edge_type = edge.getType() or ""
        if 'highway' in edge_type:  # filtrer si besoin
            shape = edge.getShape()
            mid_index = len(shape) // 2
            x_mid, y_mid = shape[mid_index]
            lon, lat = net.convertXY2LonLat(x_mid, y_mid)
            f.write(f"{edge.getID()},{lat},{lon}\n")
            count += 1  # incrémente pour chaque point écrit

print(f"✅ {count} points créés et sauvegardés dans edges_points_tomtom.txt")
