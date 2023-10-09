import requests
import json

import migrate.config.AppConfig as AppConfig

import warnings
warnings.filterwarnings('ignore')


def readDbFromSql(sqlFilePath, params=None):

    import pandas as pd

    sqlFile = open(sqlFilePath)
    query = sqlFile.read().format(params)
    
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
        dbname=AppConfig.db_details["sql_db_name"],
        user=AppConfig.db_details["sql_user_name"],
        host=AppConfig.db_details["sql_host_name"],
        port=AppConfig.db_details["sql_port_number"],
        password=AppConfig.db_details["sql_password"]
        )

    return con


def mapSqlToXml(row, fhirTemplate, mapping):
    for keys in mapping.keys():
        value = mapping[keys]
        if(isinstance(value, str)):
            keyList = keys.split('||')
            if len(keyList)>1:
                childNode = fhirTemplate
                for i in range((len(keyList) - 1)):
                    childNode = childNode[keyList[i]]
                childNode[keyList[i + 1]] = row[value]
            else:
                childNode = fhirTemplate
                childNode[keys] = row[value]
        else:
            innerData = readDbFromSql(sqlFilePath=value['sqlFilePath'], params=convertIdFromFhirToOmop(row['id']))
            for j, innerRow in innerData.iterrows():
                innerFhirTemplate = readTemplate(xmlTemplateFile=value['xmlTemplatePath'])
                for innerKeys in value['xml_sql_mapping']:
                    innerValue = value['xml_sql_mapping'][innerKeys]
                    innerKeyList = innerKeys.split('||')
                    if len(innerKeyList)>1:
                        childNode = innerFhirTemplate
                        for i in range((len(innerKeyList) - 1)):
                            childNode = childNode[innerKeyList[i]]
                        childNode[innerKeyList[i + 1]] = innerRow[innerValue]
                    else:
                        childNode = innerFhirTemplate
                        childNode[innerKeys] = row[innerValue]
            childNode = fhirTemplate
            childNode[keys] = [innerFhirTemplate]
            print('keys: ', keys)
            print('value: ', value)
    return fhirTemplate


def put(entity, data):
    fhirServerBaseUrl = AppConfig.fhir_server_base_url
    fhirUrlEntity = fhirServerBaseUrl + '/' + entity

    response = requests.put(
        url=fhirUrlEntity,
        json=data,
        headers={"Content-Type": "application/fhir+json"}
    )

    return response


def convertIdFromFhirToOmop(fhirId):
    omopId = '-' + str(fhirId)[1:] if str(fhirId).startswith('m') else str(fhirId)[1:]
    return omopId
