import json
import pandas as pd

INPUT_FILE = "jobs_7392122_results_vitesse_details_report_.json"
OUTPUT_FILE = "tomtom_clean_with_edges.json"

# Load TomTom JSON
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    report = json.load(f)

network_data = report.get("network", {})

# Map timeSet id → human-readable timeRange
time_map = {int(ts["@id"]): ts["name"] for ts in report["timeSets"]}

clean_segments = []
rows = []

for seg in network_data.get("segmentResults", []):
    seg_id = seg.get("segmentId")
    new_seg_id = seg.get("newSegmentId")
    shape = [(pt.get("latitude"), pt.get("longitude")) for pt in seg.get("shape", [])]

    time_results = []
    for tresult in seg.get("segmentTimeResults", []):
        tid = tresult.get("timeSet")
        time_range = time_map.get(tid, str(tid))
        harmonic_speed = tresult.get("harmonicAverageSpeed")
        if harmonic_speed is not None:
            time_results.append({
                "timeRange": time_range,
                "harmonicSpeed_kmh": harmonic_speed,
                "harmonicSpeed_mps": harmonic_speed / 3.6
            })

            # Add a row to DataFrame
            rows.append({
                "segmentId": seg_id,
                "newSegmentId": new_seg_id,
                "latitudes": [pt[0] for pt in shape],
                "longitudes": [pt[1] for pt in shape],
                "timeRange": time_range,
                "harmonicSpeed_kmh": harmonic_speed,
                "harmonicSpeed_mps": harmonic_speed / 3.6
            })

    clean_segments.append({
        "segmentId": seg_id,
        "newSegmentId": new_seg_id,
        "shape": shape,
        "timeResults": time_results,
        "edgeId": None  # placeholder for later matched edge
    })

# Create DataFrame
df = pd.DataFrame(rows)
df.to_csv("tomtom_dataframe.csv", index=False)

# Save clean JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump({"segments": clean_segments}, f, indent=2, ensure_ascii=False)

print(f"✅ DataFrame created with {len(df)} rows, clean JSON saved: {OUTPUT_FILE}")
