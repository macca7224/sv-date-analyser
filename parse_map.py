import argparse
import csv
import json
import os
import multiprocessing

from tqdm import tqdm

from get_date import find_accurate_timestamp

# Radius for date check
RADIUS = 30


def parse_loc(loc):
    lat, lng = loc['lat'], loc['lng']
    month = loc['imageDate']

    try:
        timestamp = find_accurate_timestamp(lat, lng, month, RADIUS)
    except Exception:
        print(f'Failed to get date for {lat}, {lng}')
        return None
    return timestamp, lat, lng


def bulk_parse(locs):
    total = len(locs)
    with multiprocessing.Pool() as pool:
        results = list(tqdm(pool.imap(parse_loc, locs), total=total))

    results = [result for result in results if result is not None]
    return results


def main(locs):
    results = bulk_parse(locs)

    name = os.path.basename(args.json_file).split('.')[0]
    output_path = f'csv/{name}.csv'
    with open(output_path, 'w') as csv_f:
        csv_writer = csv.writer(csv_f)
        csv_writer.writerow(['timestamp', 'lat', 'lng'])
        csv_writer.writerows(results)

    print(f'Saved to {output_path}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('json_file', type=str, help='Path to the JSON file')

    args = parser.parse_args()

    with open(args.json_file) as f:
        json_data = json.load(f)
        locs = json_data['customCoordinates']

    main(locs)
