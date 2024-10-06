# Flights project for Fligoo

This project takes an API related to flights, filter the results, clean the data and then upload the records to a postgres DB with the name testfligoo and populates a table named testdata

## Table of Contents
- [Project Title](## Flights project for Fligoo

A brief description of what this project does and who it's for.

## Table of Contents
- [Project Title](#project-title)
- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
- [To-do's](#todo)

## Description

We were requested to create a user using the following API service https://aviationstack.com/ where we can make an API call to retrieve certain information about different flights, 
after that an access_key is created for us so we can make the API calls. In our case we just need the flights with ACTIVE status and we limit the result to 100 records, after that we
retrieve just 9 columns that were required for this challenge.

Once we have the results from the API call we proceed to clean the data by replacing characters using pandas, then we create the table needed on a postgres instance running on a Docker container inserting the data using an Airflow DAG
that runs on a daily basis, populating the table testdata inside the testfligoo database.

Finally, we created a jupyter notebook that retrieves the records from the testdata table displaying it as a pandas dataframe

## Installation

We need to have Docker Desktop to run the code properly

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/yourproject.git](https://github.com/ulises-ASTRADA/flights-project.git
    ```
2. Navigate to the project directory:
    ```bash
    cd flights-project
    ```
3. Build the Docker image:
    ```bash
    docker-compose build
    ```

4. Start the Docker container:
    ```bash
    docker-compose up
    ```

## Usage

I recommend creating a user here https://aviationstack.com/signup/free because we will need our own access_key in case that the access_key provided changed or if it reached the free usage monthly, once you've done this change
the ACCESS_KEY value on the file flights_dag.py inside the dags folder using your own access_key.

## To do

I have some ideas for improving this challenge but I didn't have enough time to test and implement them:
 1. Idempotency: we could define a parameter (maybe something like an execution_date) so when we have to retry a task on Airflow we make sure that we get the same result for the same task.
 2. Storing credentials safely: this can be done by using environment variables on Airflow or if we are deploying this on AWS we could use boto3 to call the Secrets Manager service where we have our credentials stored
    (e.g the base URL, access_key, airflow user, password, schema, etc.)
 3. Performance: we could create partitions for each month of the year and create and index. 
