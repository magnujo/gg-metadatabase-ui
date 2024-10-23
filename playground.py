import psycopg2
from geopy.geocoders import Nominatim
import time

from constants.db_connections import PSYCON_CONFIG
from constants.db_table_related_constants import data

fs = data.field_sample



# Get latitude and longitude from the field_sample table
def get_lat_lon(conn):
    
    cursor = conn.cursor()
    query = f'SELECT "{data.field_sample.field_sample_id()}", "{fs.latitude()}", "{fs.longitude()}" FROM "{data()}"."{fs()}"'
    print(query)
    cursor.execute(query)
    return cursor.fetchall()

# Reverse geocode latitude and longitude
def reverse_geocode(lat, lon):
    geolocator = Nominatim(user_agent="db-web-app")
    location = geolocator.reverse((lat, lon), )
    return location.address if location else None

# Update the rev_geocode column with reverse geocoded address
def update_rev_geocode(conn, record_id, address):
    cursor = conn.cursor()
    query = f'UPDATE "{data()}"."{fs}" SET rev_geocode = %s WHERE {fs.field_sample_id()} = %s'
    cursor.execute(query, (address, record_id))
    conn.commit()

# Main function
def run():

    connection = psycopg2.connect(**PSYCON_CONFIG)
    with connection as conn:
        
        lat_lon_data = get_lat_lon(conn)
        for record in lat_lon_data:
            record_id, lat, lon = record
            address = reverse_geocode(lon, lat)
            print(f"Updated record {record_id} with address: {address} from lat: {lon} and lon: {lat}" )
            # if address:
            #     update_rev_geocode(conn, record_id, address)
                
            time.sleep(1)  # To prevent overloading the geocoding service


run()

