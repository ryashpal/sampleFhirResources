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
    return fhirTemplate


def get(url):
    response = requests.get(
        url=url
    )
    return response


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


def getLatestLastUpdatedTime(entity):
    response = get('http://superbugai.erc.monash.edu:8082/fhir/' + entity + '?_count=1&_sort=-_lastUpdated')
    responseJson = json.loads(response.text)
    entries = responseJson['entry']
    for entry in entries:
        if 'resource' in entry:
            if 'meta' in entry['resource']:
                if 'lastUpdated' in entry['resource']['meta']:
                    return entry['resource']['meta']['lastUpdated']
    return None


def readFhirFromUrl(urlQueryStringPath):
    response = None
    urlQueryString = None
    with open(urlQueryStringPath) as f:
        urlQueryString = f.read()
    if urlQueryString:
        response = get(urlQueryString)
    return json.loads(response.text)


def readSqlFile(sqlFilePath):
    sql = None
    with open(sqlFilePath) as f:
        sql = f.read()
    return sql


def mapJsonToSql(fhirData, mapping):
    paramsList = []
    if 'entry' in fhirData:
        entries = fhirData['entry']
        for entry in entries:
            params = {}
            if 'resource' in entry:
                for key in mapping.keys():
                    childResource = entry['resource']
                    valueList = mapping[key].split('||')
                    for i in range(len(valueList) - 1):
                        index = valueList[i]
                        if index.isdigit():
                            index = int(index)
                        childResource = childResource[index]
                    params[key] = childResource[valueList[len(valueList) - 1]]
            params['id'] = convertIdFromFhirToOmop(params['id'])
            paramsList.append(params)
    return paramsList


def updateDb(sqlQuery, params):
    con = getConnection()
    cur = con.cursor()
    cur.execute(sqlQuery, params)
    count = cur.rowcount
    con.commit()
    return count



if __name__ == "__main__":
    # print(getLatestLastUpdatedTime('Encounter'))
    # response = readFhirFromUrl(urlQueryStringPath='migrate/urls/Patient.url', id='m1918619731')
    # print('response.status_code: ', type(response.status_code))
    # print('response.text: ', response.text)
    insertSql = readSqlFile(sqlFilePath='migrate/sql/insert/Person.sql')
    print('insertSql: ', insertSql)
