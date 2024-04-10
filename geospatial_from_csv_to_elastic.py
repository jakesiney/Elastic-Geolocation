import csv
import requests
import json
import os
import sys
from dotenv import load_dotenv
from elasticsearch import Elasticsearch



load_dotenv()
elastic_cloud_id = os.getenv('ELASTIC_CLOUD_ID')
elastic_password = os.getenv('ELASTIC_PASSWORD')
API_KEY = os.getenv('google_maps_api_key')

es = Elasticsearch(
    cloud_id=elastic_cloud_id,
    basic_auth=('elastic', elastic_password)
)

def geocode(address):
    try:
        response = requests.get(f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={API_KEY}')
        if response.status_code != 200:
            print(f"HTTP error {response.status_code} for address: {address}")
            return None, None

        data = response.json()

        if data['status'] != 'OK':
            print(f"Error geocoding address '{address}': {data.get('error_message', 'Unknown error')}")
            return None, None

        results = data.get('results')
        if results:
            location = results[0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            print(f"No results for address: {address}")
            return None, None

    except Exception as e:
        print(f"Exception occurred while geocoding address '{address}': {e}")
        return None, None



def process_csv(filename):
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            address_parts = [row['Line 1'], row['Line 2'], row['Line 3'], row['Line 4'], row['Post Code']]
            address = ', '.join(part for part in address_parts if part)
            lat, lon = geocode(address)
            if lat and lon:
                data = {
                    'client_name': row['Client Name'],
                    'site_name': row['Site Name'],
                    'location': {
                        'lat': lat,
                        'lon': lon
                    }
                }
                try:
                    response = es.index(index='halo-customer-geolocation', body=data)
                    print(f'Document: {data}')
                    print(f'Elasticsearch ID: {response["_id"]}')
                except Exception as e:
                    print(f"Error indexing document: {e}")


if __name__ == '__main__':
    process_csv('sites.csv')