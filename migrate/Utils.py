import requests
import json

import Config


def readDbFromSql(sqlFilePath):

    import os
    import pandas as pd

    sqlFile = open(sqlFilePath)
    query = sqlFile.read()
    
    con = getConnection()
    df = pd.read_sql_query(query, con)
    return df


def readTemplate(xmlTemplateFile):
    with open(xmlTemplateFile) as f:
        jsonTemplate = f.read()
    return json.loads(jsonTemplate)


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


def mapSqlToXml(row, fhirTemplate, mapping):
    for keys in mapping.keys():
        fhirTemplate[keys] = row[mapping[keys]]
    return fhirTemplate


def put(entity, data):
    fhirServerBaseUrl = Config.fhir_server_base_url
    fhirUrlEntity = fhirServerBaseUrl + '/' + entity

    response = requests.put(
        url=fhirUrlEntity,
        json=data,
        headers={"Content-Type": "application/fhir+json"}
    )
    return response
