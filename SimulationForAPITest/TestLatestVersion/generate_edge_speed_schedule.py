import json

def get_speeds_by_timeline(json_file_path):
    """
    Reads a JSON file, extracts edgeId and time-based speeds,
    and returns a dictionary of the data.
    """
    speeds_by_timeline = {}

    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)

        for segment in data['segments']:
            edge_id = segment.get('edgeId')
            if edge_id:
                if edge_id not in speeds_by_timeline:
                    speeds_by_timeline[edge_id] = {}

                for time_result in segment.get('timeResults', []):
                    time_range = time_result.get('timeRange')
                    harmonic_speed_mps = time_result.get('harmonicSpeed_mps')

                    if time_range and harmonic_speed_mps is not None:
                        speeds_by_timeline[edge_id][time_range] = harmonic_speed_mps

    except FileNotFoundError:
        print(f"Error: The file '{json_file_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{json_file_path}'.")

    return speeds_by_timeline

# The path to your matched data file
input_file_path = 'tomtom_matched_edges.json'
output_file_path = 'sumo_edge_speeds.json'

# Get the organized speed data
edge_speed_data = get_speeds_by_timeline(input_file_path)

# Write the data to a new JSON file
if edge_speed_data:
    with open(output_file_path, 'w') as out_file:
        json.dump(edge_speed_data, out_file, indent=4)
    print(f"Data successfully written to '{output_file_path}'")
else:
    print("No data was processed, so no output file was created.")