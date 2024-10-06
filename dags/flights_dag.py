from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import pandas as pd


#Here we define the constants to connect to the API
ACCESS_KEY = '13824a221d87297fe2e6bc3c8ee20a94'
BASE_URL = 'https://api.aviationstack.com/v1/'


def fetch_flights_data():

    api_result = requests.get(f'{BASE_URL}flights?access_key={ACCESS_KEY}&limit=100&flight_status=active')

    flights = api_result.json()

    #Here we access the columns we are interested in
    flights_data = flights['data']

    #We create an empty list to save the records
    collected_data = []

    for flight in flights_data:
        flight_info = {
            'flight_date': flight['flight_date'],
            'flight_status': flight['flight_status'],
            'departure_airport': flight['departure']['airport'],
            'departure_timezone': flight['departure']['timezone'],
            'arrival_airport': flight['arrival']['airport'],
            'arrival_timezone' : flight['arrival']['timezone'],
            'arrival_terminal' : flight['arrival']['terminal'],
            'airline_name': flight['airline']['name'],
            'flight_number': flight['flight']['number']
        }

        collected_data.append(flight_info)
        collected_data_to_df = pd.DataFrame(collected_data)
        number_of_rows = len(collected_data_to_df)
        print(f'Data fetched containing {number_of_rows} rows')
    return collected_data