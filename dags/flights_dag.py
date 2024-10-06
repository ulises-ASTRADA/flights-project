from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import pandas as pd
import psycopg2


# Define the constants to connect to the API
ACCESS_KEY = '13824a221d87297fe2e6bc3c8ee20a94'
BASE_URL = 'https://api.aviationstack.com/v1/'


def fetch_flights_data(**kwargs):

    api_result = requests.get(f'{BASE_URL}flights?access_key={ACCESS_KEY}&limit=100&flight_status=active')

    flights = api_result.json()

    # Access the columns we are interested in
    flights_data = flights['data']

    collected_data = []

    for flight in flights_data:
        flight_info = {
            'flight_date': flight['flight_date'],
            'flight_status': flight['flight_status'],
            'departure_airport': flight['departure']['airport'],
            'departure_timezone': flight['departure']['timezone'],
            'arrival_airport': flight['arrival']['airport'],
            'arrival_timezone': flight['arrival']['timezone'],
            'arrival_terminal': flight['arrival'].get('terminal', None),  # If there are no terminal values
            'airline_name': flight['airline']['name'],
            'flight_number': flight['flight']['number']
        }
        collected_data.append(flight_info)

    collected_data_to_df = pd.DataFrame(collected_data)
    print(collected_data_to_df)

    # Convert the DataFrame to a dictionary for the Xcom
    kwargs['ti'].xcom_push(key='collected_data', value=collected_data_to_df.to_dict(orient='records'))
    return collected_data_to_df


def upload_to_db(**kwargs):

    collected_data = kwargs['ti'].xcom_pull(task_ids='fetch_flights_data', key='collected_data')

    # Convert the data back to a DataFrame and replace the / for a - as requested
    collected_data_to_df = pd.DataFrame(collected_data)
    collected_data_to_df['arrival_terminal'] = collected_data_to_df['arrival_terminal'].replace('/', '-', regex=True)
    collected_data_to_df['departure_timezone'] = collected_data_to_df['departure_timezone'].replace('/', '-', regex=True)
    
    conn = psycopg2.connect(
        dbname="testfligoo",
        user="airflow",
        password="airflow",
        host="postgres",
        port="5432"
    )
    cursor = conn.cursor()
    
    # Creating the table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS testdata (
        flight_date DATE,
        flight_status VARCHAR,
        departure_airport VARCHAR,
        departure_timezone VARCHAR,
        arrival_airport VARCHAR,
        arrival_timezone VARCHAR,
        arrival_terminal VARCHAR,
        airline_name VARCHAR,
        flight_number TEXT DEFAULT 'UNKNOWN'
    );
    """)

    conn.commit()

    # Inserting rows into the table
    for index, row in collected_data_to_df.iterrows():
        cursor.execute(
            """
            INSERT INTO testdata 
            (flight_date, flight_status, departure_airport, departure_timezone, arrival_airport, arrival_timezone, arrival_terminal, airline_name, flight_number) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (row['flight_date'], row['flight_status'], row['departure_airport'], row['departure_timezone'],
             row['arrival_airport'], row['arrival_timezone'], row['arrival_terminal'], row['airline_name'],
             row['flight_number'])
        )

    conn.commit()

    # Logging of the SELECT query
    cursor.execute("SELECT * FROM testdata;")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

    cursor.close()
    conn.close()

    print("Data inserted and selected successfully!")

# We create the Airflow DAG
with DAG('flight_data_pipeline', start_date=datetime(2024, 10, 5), schedule_interval='@daily') as dag:
    
    fetch_task = PythonOperator(
        task_id='fetch_flights_data',
        python_callable=fetch_flights_data,
        provide_context=True
    )
    
    insert_task = PythonOperator(
        task_id='upload_to_db',
        python_callable=upload_to_db,
        provide_context=True
    )

    fetch_task >> insert_task
