from tqdm import tqdm

from migrate.Utils import readDbFromSql
from migrate.Utils import readTemplate
from migrate.Utils import mapSqlToXml
from migrate.Utils import put

import logging

log = logging.getLogger("EHRQC")


def fhirToOmop():
    pass


def omopToFhir(entity, sqlFilePath, xmlTemplatePath, mapping):
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
        response = put(entity + '/' + str(row.id), fhirJson)
        log.debug('response: ' + str(response.text))
