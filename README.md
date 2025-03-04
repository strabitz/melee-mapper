# melee-mapper

This is a script that generates a map from each of the attendees for a
tournament hosted on start.gg

## Setup
Clone this repo then install dependencies with

`pip install -r requirements.txt`

Then in the script, add your start.gg key and tournament slug to the constants
at the top. The slug should look like this: "tournament/melee-in-the-park-1/event/melee-singles"

## Running the script

Simply run

`python get-players-location.py`

Then view the resulting "map.html" file in your web browser.

