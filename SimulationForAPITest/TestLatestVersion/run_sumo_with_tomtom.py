import json
import traci
import sumolib

CLEAN_JSON = "tomtom_matched_edges.json"
SUMO_BINARY = "sumo-gui"  # or "sumo"
NET_FILE = "H2ST8.net.xml"
ROUTE_FILE = "routes.rou.xml"

# Load cleaned data
with open(CLEAN_JSON, "r") as f:
    tomtom_data = json.load(f)["segments"]

# Map edgeId → timeline speeds
edge_speed_map = {}
for seg in tomtom_data:
    edge_id = seg["edgeId"]
    if not edge_id:
        continue
    edge_speed_map[edge_id] = seg["timeResults"]

# Start SUMO
traci.start([SUMO_BINARY,
             "-n", NET_FILE,
             "-r", ROUTE_FILE])

# Example: simple mapping from SUMO time to TomTom "timeRange"
# Here we assume simulation starts at 0 sec = 00:00, each hour = 3600 sec.
# You will adapt depending on your dataset and scenario.
def get_speed_for_edge(edge_id, sim_time):
    if edge_id not in edge_speed_map:
        return None
    hour = (sim_time // 3600) % 24
    for tr in edge_speed_map[edge_id]:
        start, end = tr["timeRange"].split("-")
        start_h = int(start.split(":")[0])
        end_h = int(end.split(":")[0])
        if start_h <= hour < end_h:
            return tr["harmonicSpeed_mps"]
    return None

# Main loop
step = 0
while step < 3600 * 24:  # simulate one day
    traci.simulationStep()
    for edge_id in edge_speed_map:
        speed = get_speed_for_edge(edge_id, step)
        if speed:
            traci.edge.setMaxSpeed(edge_id, speed)
    step += 1

traci.close()
