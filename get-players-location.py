import requests
import folium
from geopy.geocoders import Nominatim
import os
import time
import json


API_KEY = "<PLACE_KEY_HERE>"
API_URL = "https://api.start.gg/gql/alpha"
TOURNAMENT_SLUG = "<PLACE_SLUG_HERE>"

def generate_map(locations):
    # center on US
    m = folium.Map(location=[39.50, -98.35], zoom_start=4)
    geolocator = Nominatim(user_agent="melee_mapper")

    for city_state in locations:
        try:
            location = geolocator.geocode(city_state)
            if location:
                lat, lon = location.latitude, location.longitude
                folium.Marker([lat, lon], popup=city_state).add_to(m)
                print(f"Added marker for {city_state}: {lat}, {lon}")
            else:
                print(f"Location not found for: {city_state}")
            # Sleep to respect the geocoder's usage policy
            time.sleep(1)
        except Exception as e:
            print(f"Error geocoding {city_state}: {e}")

    return m

def get_event_id(slug):
    query = """
    query getEventId($slug: String) {
        event(slug: $slug) {
            id
            name
        }
    }
    """
    data = run_query(query, {"slug": slug})
    return data["data"]["event"]["id"]


def get_players_from_event(event_id):
    players = []
    page = 1
    
    while True:
        query = """
        query getEntrants($eventId: ID!, $page: Int!) {
            event(id: $eventId) {
                entrants(query: { page: $page, perPage: 50 }) {
                    nodes {
                        participants {
                            user {
                                name
                                location {
                                    city
                                    state
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        response = run_query(query, {"eventId": event_id, "page": page})
        entrants = response["data"]["event"]["entrants"]["nodes"]
        
        if not entrants:
            break  # No more pages to fetch
        
        for entrant in entrants:
            for participant in entrant["participants"]:
                user = participant.get("user")
                if user:
                    players.append({
                        "name": user["name"],
                        "city": user["location"].get("city"),
                        "state": user["location"].get("state")
                    })
        
        page += 1
    
    return players


def run_query(query, variables):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    response = requests.post(API_URL, json={"query": query, "variables": variables}, headers=headers)
    return response.json()


def get_locations():
    event_id = get_event_id(TOURNAMENT_SLUG)
    all_players = get_players_from_event(event_id)
    locations = set()
    for player in all_players:
        city = player['city']
        state = player['state']
        if city and state:
            locations.add(f'{city}, {state}')
    return locations


def main():
    # Get locations
    locations = get_locations()

    # Generate the map
    map_obj = generate_map(locations)
    map_obj.save("map.html")
    print("Map has been saved to map.html")

if __name__ == "__main__":
    main()
