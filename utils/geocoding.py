from googlemaps import Client as GoogleMaps
import pandas as pd
import sys
sys.path.append('keys/')
from keys import geocoding_api

def geocoding(df) :
    print('Generando lat long a partir de dirección...')
    df['long'] = ""
    df['lat'] = ""
    gmaps = GoogleMaps(geocoding_api)
    for x in range(len(df)):
        try:
            geocode_result = gmaps.geocode(df['direccion'].values[x])
            df['lat'][x] = geocode_result[0]['geometry']['location']['lat']
            df['long'][x] = geocode_result[0]['geometry']['location']['lng']
        except IndexError:
            print("Geocoding: Address was wrong...")
        except Exception as e:
            print("Geocoding: Unexpected error occurred.", e )
    print('Geocoding finalizado!')
    return df
