# SV Date Analyser

Tool to analyse dates and determine the path taken by a driver from Google
Street View locations.

Uses the technique found by [Emily](https://github.com/itisem) to determine the
exact timestamp for locations.

![image](https://github.com/macca7224/sv-date-analyser/assets/138291010/507b069d-be15-416d-987b-46c90a0d9308)

## Setup
1. `git clone https://github.com/macca7224/sv-date-analyser`
2. `pip install -r requirements.txt`

## Getting dates from a generated map
 - Generate a map using https://map-generator-nsj.vercel.app/ **(ensure check all dates is turned off)**
 - Export to JSON and save the file somewhere (a maps directory exists for this purpose but it can be anywhere)
 - Run `python parse_map.py <map>.json`
 - The output will be saved as a CSV file with the format `timestamp,lat,lng` in `csv/<map>.csv`

## Analysing the path taken
 - Run `python get_path.py csv/<map.csv> <segment gap (minutes)>`
 - The segment gap is threshold for the time between locations to be considered
 separate segments. e.g. if it's set to 10, anywhere with a gap of more than 10
 minutes between locations will be considered separate segments. Generally a few
 hours works well but if you want to see exactly when the driver stops and starts
 again put it lower
 - This will generate an HTML file containing the map and save it as `<map>_path.html`
 (it should also open in your browser automatically)
 - Hover over the button in the top right to toggle which segments are visible.
 Doing one at a time generally works well
 - Note: you'll likely get bad results if multiple cars were driving simultaneously

## Example usage
`python parse_map.py maps/birdsville.json`

`python get_path.py csv/birdsville.csv`


