from tqdm import tqdm

from migrate.Utils import readDbFromSql
from migrate.Utils import readTemplate
from migrate.Utils import mapSqlToXml
from migrate.Utils import readFhirFromUrl
from migrate.Utils import readSqlFile
from migrate.Utils import mapJsonToSql
from migrate.Utils import put

import logging

log = logging.getLogger("EHRQC")


def fhirToOmop(id, entity, urlQueryStringPath, sqlFilePath, mapping, save=False, savePath='./'):
    log.info('Starting FHIR to OMOP for ' + entity)
    log.info('urlQueryStringPath: ' + urlQueryStringPath)
    log.info('sqlFilePath: ' + sqlFilePath)
    log.info('mapping: ' + str(mapping))
    log.info('save: ' + str(save))
    log.info('savePath: ' + str(savePath))
    log.info('Fetching data from FHIR')
    fhirData = readFhirFromUrl(urlQueryStringPath, id)
    log.debug('fhirData: ' + str(fhirData))
    log.info('Reading SQL file')
    insertQuery = readSqlFile(sqlFilePath)
    log.debug('insertQuery: ' + str(insertQuery))
    log.info('Performing mapping')
    params = mapJsonToSql(fhirData, mapping)
    log.debug('params: ' + str(params))


# rename XML to JSON everywhere in this function
def omopToFhir(entity, sqlFilePath, xmlTemplatePath, mapping): # add an additional argument to specify if its needed to be saved
    log.info('Starting OMOP to FHIR for ' + entity)
    log.info('sqlFilePath: ' + sqlFilePath)
    log.info('xmlTemplatePath: ' + xmlTemplatePath)
    log.info('mapping: ' + str(mapping))
    omopData = readDbFromSql(sqlFilePath)
    log.debug('omopData: ' + str(omopData))
    fhirTemplate = readTemplate(xmlTemplateFile=xmlTemplatePath)
    log.debug('fhirTemplate: ' + str(fhirTemplate))
    for i, row in tqdm(omopData.iterrows(), total=omopData.shape[0]):
        log.debug('i: ' + str(i))
        log.debug('row: ' + str(row))
        fhirJson = mapSqlToXml(row, fhirTemplate, mapping)
        log.debug('fhirJson: ' + str(fhirJson))
        response = put(entity + '/' + str(row.id), fhirJson) # move this line to Utility fucntion
        log.debug('response: ' + str(response.text))
