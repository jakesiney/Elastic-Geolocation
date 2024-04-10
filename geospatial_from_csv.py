import csv
import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('google_maps_api_key')

def geocode(address):
    # Use Google Maps Geocoding API to get the latitude and longitude
    response = requests.get(f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key=API_KEY')
    data = response.json()
    return data['results'][0]['geometry']['location']['lat'], data['results'][0]['geometry']['location']['lng']

addresses = []
with open('Site_Address List.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        address = ', '.join([row['Line 1'], row['Line 2'], row['Line 3'], row['Line 4'], row['Post Code']])
        lat, lon = geocode(address)
        addresses.append({
            'name': row['Site Name'],
            'location': {
                'lat': lat,
                'lon': lon
            }
        })

with open('addresses.json', 'w') as file:
    json.dump(addresses, file)