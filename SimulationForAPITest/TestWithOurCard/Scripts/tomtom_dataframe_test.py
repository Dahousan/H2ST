import requests
import pandas as pd
from datetime import datetime
import json
import os
import time

API_KEY = '69qsRhlXsdxbsM5iSpccojm5sqWYYyEH'  

POINTS_FILE = 'data/filtered_intersections_all_zones.json'
OUTPUT_DIR = 'api_dataframe'

def get_tomtom_data(lat, lon):
    url = (
        'https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json'
        f'?point={lat},{lon}'
        f'&unit=KMPH&openLr=false&key={API_KEY}'
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur API ({response.status_code}) pour le point {lat},{lon} - {response.text}")
        return None

def parse_data_light(json_data, zone, query_lat, query_lon):
    flow = json_data.get('flowSegmentData', {})
    return {
        'zone': zone,
        'point_origin_lat': query_lat,
        'point_origin_lon': query_lon,
        'speed': flow.get('currentSpeed', None),
        'free_flow_speed': flow.get('freeFlowSpeed', None),
        'congestion_level': flow.get('currentTravelTime', None),
        'timestamp': datetime.utcnow().isoformat()
    }

def parse_data_detailed(json_data, zone, query_lat, query_lon):
    flow = json_data.get('flowSegmentData', {})

    coords = flow.get('coordinates', {}).get('coordinate', [])
    segment_coords = []
    for c in coords:
        segment_coords.append({'lat': c.get('latitude'), 'lon': c.get('longitude')})

    return {
        'zone': zone,
        'point_from_file': {'lat': query_lat, 'lon': query_lon},
        'segment_coordinates': segment_coords,
        'speed': flow.get('currentSpeed', None),
        'free_flow_speed': flow.get('freeFlowSpeed', None),
        'congestion_level': flow.get('currentTravelTime', None),
        'timestamp': datetime.utcnow().isoformat()
    }

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(POINTS_FILE, 'r', encoding='utf-8') as f:
        zones_data = json.load(f)

    records_light = []
    records_detailed = []

    for zone_data in zones_data:
        zone = zone_data['zone']
        points = zone_data['points']
        for pt in points:
            lat, lon = pt['lat'], pt['lon']
            json_resp = get_tomtom_data(lat, lon)
            if json_resp:
                records_light.append(parse_data_light(json_resp, zone, lat, lon))
                records_detailed.append(parse_data_detailed(json_resp, zone, lat, lon))
            time.sleep(1)  

    # Sauvegarde DataFrame 
    df_light = pd.DataFrame(records_light)
    csv_path = os.path.join(OUTPUT_DIR, 'tomtom_traffic_data_light.csv')
    json_light_path = os.path.join(OUTPUT_DIR, 'tomtom_traffic_data_light.json')
    excel_path = os.path.join(OUTPUT_DIR, 'tomtom_traffic_data_light.xlsx')
    df_light.to_csv(csv_path, index=False)
    df_light.to_json(json_light_path, orient='records', force_ascii=False, indent=2)
    df_light.to_excel(excel_path, index=False)
    print(f"Données légères sauvegardées dans :\n- {csv_path}\n- {excel_path}")

    # Sauvegarde JSON détaillé complet
    json_path = os.path.join(OUTPUT_DIR, 'tomtom_traffic_data_detailed.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(records_detailed, f, ensure_ascii=False, indent=2)
    print(f"Données détaillées sauvegardées dans : {json_path}")

if __name__ == '__main__':
    main()
