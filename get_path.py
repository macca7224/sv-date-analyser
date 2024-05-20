import argparse
import math
import webbrowser

import folium
import pandas as pd


def add_arrows(map_obj, coordinates, timestamps, color='blue', size=4):
    for i in range(1, len(coordinates)):
        p1, p2 = coordinates[i-1], coordinates[i]
        t1, t2 = timestamps[i-1], timestamps[i]
        tooltip_text = f'{t1}<br>-><br>{t2}'

        folium.PolyLine([p1, p2], color=color, tooltip=tooltip_text).add_to(map_obj)

        # Calculate the angle for the arrow
        angle = math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))

        # Add the arrow marker
        arrow = folium.RegularPolygonMarker(
            location=[(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2],
            fill_color=color,
            number_of_sides=3,
            radius=size,
            rotation=angle - 90,
            tooltip=tooltip_text
        )
        arrow.add_to(map_obj)


def process_data(file_path, segment_gap):
    data = pd.read_csv(file_path)

    # Convert timestamp column to datetime and sort by timestamp
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='s')
    data = data.sort_values(by='timestamp')

    # Calculate time differences and segment the data
    data['time_diff'] = data['timestamp'].diff().dt.total_seconds()
    data['segments'] = (data['time_diff'] > segment_gap * 60).cumsum()
    data.drop(columns=['time_diff'], inplace=True)

    return data


def main(file_path, segment_gap):
    data = process_data(file_path, segment_gap)

    # Extract segments as lists of coordinates and timestamps
    segments = [
        (list(zip(segment.lat, segment.lng)), segment.timestamp.tolist())
        for _, segment in data.groupby('segments')
    ]

    # Create a map centered on the first coordinate
    m = folium.Map(location=[data.lat.iloc[0], data.lng.iloc[0]], zoom_start=14, tiles=None)

    # Add Google Maps tile layer
    folium.TileLayer(
        tiles='https://{s}.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}',
        attr='Google Maps',
        subdomains=['mt0', 'mt1', 'mt2', 'mt3'],
        max_zoom=26,
        max_native_zoom=22,
        name='Google Maps'
    ).add_to(m)

    # Add each segment as a separate layer with arrows
    for i, (segment, timestamps) in enumerate(segments):
        segment_layer = folium.FeatureGroup(name=f'Segment {i+1}')
        add_arrows(segment_layer, segment, timestamps)
        
        # Add start and end markers for each segment
        folium.Marker(
            location=segment[0],
            popup=f'Start Segment {i+1}<br>{timestamps[0]}',
            icon=folium.Icon(color='green')
        ).add_to(segment_layer)
        folium.Marker(
            location=segment[-1],
            popup=f'End Segment {i+1}<br>{timestamps[-1]}',
            icon=folium.Icon(color='red')
        ).add_to(segment_layer)
        
        segment_layer.add_to(m)

    # Add layer control for toggling segments
    folium.LayerControl().add_to(m)

    # Save the map to an HTML file
    file_name = file_path.split('/')[-1].split('.')[0]
    output_file = f'{file_name}_path.html'
    m.save(output_file)
    print(f'Saved to {output_file}')
    webbrowser.open(output_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('csv_file', type=str, help='Path to the CSV file')
    parser.add_argument('segment_gap', type=int, help='Gap between locs to be considered as different segments (in minutes)')

    args = parser.parse_args()
    main(args.csv_file, args.segment_gap)
