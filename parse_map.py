import argparse
import asyncio
import csv
import json
import os

from tqdm import tqdm

from get_date import find_accurate_timestamp

# Radius for date check
RADIUS = 30

# Increasing this will make the script faster, but you may get rate limited or 
# have requests fail
CHUNK_SIZE = 15


async def parse_loc(loc, progress):
    lat, lng = loc['lat'], loc['lng']
    month = loc['imageDate']

    try:
        timestamp = await find_accurate_timestamp(lat, lng, month, RADIUS)
    except Exception:
        print(f'Failed to get date for {lat}, {lng}')
        progress.update(1)
        return None
    progress.update(1)
    return timestamp, lat, lng


async def bulk_parse(locs):
    total = len(locs)
    chunks = [locs[i:i + CHUNK_SIZE] for i in range(0, total, CHUNK_SIZE)]
    
    results = []
    progress = tqdm(total=total)
    
    for chunk in chunks:
        tasks = [asyncio.create_task(parse_loc(loc, progress)) for loc in chunk]
        chunk_results = await asyncio.gather(*tasks)
        results.extend([res for res in chunk_results if res is not None])

    progress.close()
    return results


async def main(locs):
    results = await bulk_parse(locs)

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

    asyncio.run(main(locs))
