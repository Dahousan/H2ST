import traci
import sumolib
import requests
import time

# --- CONFIGURATION ---
API_KEY = "69qsRhlXsdxbsM5iSpccojm5sqWYYyEH"  
API_URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/relative0/10/json"
POINTS_FILE = "data/filtered_points_tomtom.txt"  
NET_FILE = "H2ST.net.xml"
SUMO_CONFIG = "H2ST.sumocfg"

# --- Charger le réseau SUMO via sumolib ---
net = sumolib.net.readNet(NET_FILE)

# --- Charger la correspondance edge → coordonnées GPS ---
edge_points = []
with open(POINTS_FILE) as f:
    for line in f:
        edge_id, lat, lon = line.strip().split(",")
        edge_points.append((edge_id, float(lat), float(lon)))

print(f"✅ {len(edge_points)} edges chargés depuis {POINTS_FILE}")

# --- Fonction pour récupérer la vitesse depuis TomTom ---
def get_speed_ratio(lat, lon):
    """Retourne le ratio vitesse_actuelle / vitesse_libre."""
    try:
        params = {"point": f"{lat},{lon}", "key": API_KEY, "unit": "KMPH"}
        res = requests.get(API_URL, params=params)
        if res.status_code != 200:
            return 1.0
        data = res.json().get("flowSegmentData", {})
        current = data.get("currentSpeed")
        freeflow = data.get("freeFlowSpeed")
        if current is None or freeflow in (None, 0):
            return 1.0
        return current / freeflow
    except Exception as e:
        print(f"⚠️ Erreur API: {e}")
        return 1.0

# --- Lancer SUMO en mode GUI ---
traci.start(["sumo-gui", "-c", SUMO_CONFIG, "--step-length", "1"])
print("🚦 Simulation démarrée avec SUMO-GUI")

# --- Charger les vitesses de base des edges via TraCI ---
base_speeds = {}
for edge_id, _, _ in edge_points:
    try:
        lanes = traci.edge.getLanes(edge_id)
        if lanes:
            # Récupérer la vitesse max de la première voie (lane)
            base_speeds[edge_id] = traci.lane.getMaxSpeed(lanes[0])
        else:
            # Valeur par défaut si pas de voies (par ex. 50 km/h = 13.9 m/s)
            base_speeds[edge_id] = 13.9
    except Exception as e:
        print(f"⚠️ Could not get base speed for edge {edge_id}: {e}")
        base_speeds[edge_id] = 13.9

print("✅ Base speeds loaded for edges.")

# --- Boucle principale de simulation ---
step = 0
max_steps = 100
while traci.simulation.getMinExpectedNumber() > 0 and step < max_steps:
    print(f"\n--- Étape {step} ---")
    
    # Limiter nombre d'appels API (ajuster selon votre quota)
    for edge_id, lat, lon in edge_points[:10]:
        ratio = get_speed_ratio(lat, lon)
        base_speed = base_speeds.get(edge_id, 13.9)
        new_speed = base_speed * ratio
        
        try:
            traci.edge.setMaxSpeed(edge_id, new_speed)
            print(f"  Edge {edge_id}: ratio {ratio:.2f}, speed set to {new_speed:.1f} m/s")
        except Exception as e:
            print(f"⚠️ Could not set speed for edge {edge_id}: {e}")
    
    traci.simulationStep()
    time.sleep(1)  # synchronisation temps réel
    step += 1

traci.close()
print("\n✅ Simulation terminée.")
