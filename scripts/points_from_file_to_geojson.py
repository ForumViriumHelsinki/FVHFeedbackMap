__doc__ = """
Convert input file(s) contents to a geojson file.
Input files are jsonl (json lines) and expected to be in the following format:

{
  "device_id": "ABCDABCDABCD0003",
  "lat": 60.220328,
  "lon": 25.002846,
  "comment": "",
  "button_position": 5,
  "time_received": "2024-03-07T18:50:07.581000+00:00",
  "time_pressed": "2024-03-07T18:50:07+00:00"
}

Command line arguments:
- input file(s) (jsonl)
- output file (geojson)
- button_position mapping in format: 1:"Tarvitaan penkki" 2:"Roska-astia täynnä" etc

Example usage:
python scripts/points_from_file_to_geojson.py --input-files data.jsonl --output-file data.geojson \
  --button-position-mapping 1:"Tarvitaan penkki" 2:"Roska-astia täynnä" 3:"Kukat kaipaa kastelua"

"""

import argparse
import json
import pathlib


def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-files", nargs="+", type=str, help="Input file(s) to read"
    )
    parser.add_argument("--output-file", required=False, help="Output file to write")
    parser.add_argument(
        "--button-position-mapping", nargs="+", type=str, help="Button position mapping"
    )
    parser.add_argument(
        "--ignore-unmapped",
        action="store_true",
        help="Ignore unmapped button positions",
    )
    return parser.parse_args()


def create_position_mapping(mappings: list) -> dict:
    """
    Convert mapping to a dict. Mapping is a list of strings like:
    ['1:"Tarvitaan penkki"', '2:"Roska-astia täynnä"', '3:"Kukat kaipaa kastelua"']
    """
    mapping = {}
    if mappings:
        for m in mappings:
            key, value = m.split(":")
            mapping[key] = value.strip('"')
    return mapping


def main():
    args = get_args()
    button_position_mapping = create_position_mapping(args.button_position_mapping)

    features = []
    for input_file in args.input_files:
        with open(input_file, "r") as f:
            for line in f:
                data = json.loads(line)
                button_position = button_position_mapping.get(
                    str(data["button_position"])
                )
                if button_position is None:
                    if args.ignore_unmapped:
                        continue
                    button_position = f"Unmapped: {data['button_position']}"
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [data["lon"], data["lat"]],
                    },
                    "properties": {
                        "device_id": data["device_id"],
                        "comment": data["comment"],
                        "button_position": button_position,
                        "time_received": data["time_received"],
                        "time_pressed": data["time_pressed"],
                    },
                }
                features.append(feature)

    geojson = {"type": "FeatureCollection", "features": features}
    output_file = args.output_file
    if args.output_file == "-":
        print(json.dumps(geojson, indent=2))
    elif args.output_file is None:
        output_file = pathlib.Path(args.input_files[0]).with_suffix(".geojson")
    with open(output_file, "w") as f:
        json.dump(geojson, f, indent=2)


if __name__ == "__main__":
    main()
