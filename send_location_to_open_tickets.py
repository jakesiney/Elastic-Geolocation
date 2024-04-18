from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, scan
from dotenv import load_dotenv
import os

load_dotenv()
elastic_cloud_id = os.getenv('ELASTIC_CLOUD_ID')
elastic_password = os.getenv('ELASTIC_PASSWORD')

es = Elasticsearch(
    cloud_id=elastic_cloud_id,
    basic_auth=('elastic', elastic_password)
)

# def check_location_data_format():
#     """Check the format of the location data in the 'halo-customer-geolocation' index. DEBUGGING PURPOSES ONLY."""
#     query = {
#         "query": {
#             "match_all": {}
#         }
#     }

#     results = scan(es, index="halo-customer-geolocation", query=query)
#     for result in results:
#         print(result['_source']['location'])



def fetch_location_data():
    """Fetch location data from 'halo-customer-geolocation' index and create a mapping dictionary."""
    query = {
        "query": {
            "match_all": {}
        }
    }

    results = scan(es, index="halo-customer-geolocation", query=query)
    location_map = {result['_source']['site_id']: result['_source']['location'] for result in results}
    return location_map


def update_tickets(location_map):
    """Update ticket documents in 'halo-tickets-from-api-open' index with location data."""
    def generate_updates():
        query = {
            "query": {
                "match_all": {}
            }
        }

        for ticket in scan(es, index="halo-tickets-from-api-open", query=query):
            site_id = str(ticket['_source'].get('site_id'))
            location = location_map.get(site_id)
            if location:
                yield {
                    '_op_type': 'update',
                    '_index': 'halo-tickets-from-api-open',
                    '_id': ticket['_id'],
                    'doc': {'geo_location': location}
                }
            else:
                print(f"No location data found for site_id: {site_id}")

    try:
        bulk(es, generate_updates())
        es.indices.refresh(index='halo-tickets-from-api-open')
    except Exception as e:
        print(f"Error during bulk update: {e}")


location_map = fetch_location_data()
update_tickets(location_map)
print("Ticket documents in 'halo-tickets-from-api-open' updated with location data.")


