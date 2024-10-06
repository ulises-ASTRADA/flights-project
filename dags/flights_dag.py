from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import pandas as pd
import psycopg2


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


def upload_to_db(**kwargs):
    collected_data = kwargs['ti'].xcom_pull(task_ids='fetch_flights_data')

    conn = psycopg2.connect(
        dbname="testfligoo",
        user="airflow",
        password="airflow",
        host="postgres",
        port="5432"
    )
    cursor = conn.cursor()
    
    # Here we create the table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS testdata (
        flight_date DATE NOT NULL,
        flight_status VARCHAR,
        departure_airport VARCHAR,
        departure_timezone VARCHAR,
        arrival_airport VARCHAR,
        arrival_timezone VARCHAR,
        arrival_terminal VARCHAR,
        airline_name VARCHAR,
        flight_number TEXT NOT NULL,
        PRIMARY KEY (flight_date, flight_number)
    );
    """)

    conn.commit()


    for flight, value in collected_data.iterrows():
        cursor.execute(
            "INSERT INTO people (flight_date, flight_status, departure_airport, departure_timezone, arrival_airport, arrival_timezone, arrival_terminal, airline_name, flight_number) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (value['flight_date'], value['flight_status'], value['departure_airport'], value['departure_timezone'], value['arrival_airport'], value['arrival_timezone'], value['arrival_terminal'], value['airline_name'], value['flight_number'])
        )
    
    cursor.close()
    conn.close()

    print("Data inserted successfully!")