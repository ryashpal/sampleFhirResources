import json

from tqdm import tqdm

from Utils import readDbFromSql
from Utils import readTemplate
from Utils import mapSqlToXml
from Utils import put

import logging

log = logging.getLogger("EHRQC")


def fhirToOmop():
    pass


def omopToFhir(entity, sqlFilePath, xmlTemplatePath, mapping): # test this function with organisation first
    log.info('Starting OMOP to FHIR for ' + entity)
    log.info('sqlFilePath: ' + sqlFilePath)
    log.info('xmlTemplatePath: ' + xmlTemplatePath)
    log.info('mapping: ' + str(mapping))
    omopData = readDbFromSql(sqlFilePath)
    log.info('omopData:' + str(omopData))
    fhirTemplate = readTemplate(xmlTemplateFile=xmlTemplatePath)
    log.info('fhirTemplate:' + str(fhirTemplate))
    for i, row in tqdm(omopData.iterrows(), total=omopData.shape[0]):
        log.info('i: ' + str(i))
        log.info('row: ' + str(row))
        fhirJson = mapSqlToXml(row, fhirTemplate, mapping)
        log.info('fhirJson: ' + str(fhirJson))
        response = put(entity + '/' + str(row.id), fhirJson)
        log.info('response: ' + str(response.text))
