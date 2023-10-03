import requests

import Config


fhirServerBaseUrl = Config.fhir_server_base_url


def post(entity, data):
    # Post full bundle, no restriction on bundle size
    fhirUrlEntity = fhirServerBaseUrl + '/' + entity
    response = requests.post(
        fhirUrlEntity,
        json=data,
        headers={"Content-Type": "application/fhir+json"}
    )
    return response


def put(entity, data):
    fhirUrlEntity = fhirServerBaseUrl + '/' + entity

    response = requests.put(
        url=fhirUrlEntity,
        json=data,
        headers={"Content-Type": "application/fhir+json"}
    )
    return response


def get(url):
    response = requests.get(
        url=url
    )
    return response


def delete(url):
    response = requests.delete(
        url=url
    )
    return response


def getConnection():

    import psycopg2
    # Connect to postgres with a copy of the MIMIC-III database
    con = psycopg2.connect(
        dbname=Config.db_details["sql_db_name"],
        user=Config.db_details["sql_user_name"],
        host=Config.db_details["sql_host_name"],
        port=Config.db_details["sql_port_number"],
        password=Config.db_details["sql_password"]
        )

    return con


def convertIdFromOmopToFhir(omopId):
    fhirId = 'm' + str(omopId)[1:] if str(omopId).startswith('-') else 'p' + str(omopId)
    return fhirId
