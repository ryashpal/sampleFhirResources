import uuid
import json

import pandas as pd

from models.Location import Location
from models.Encounter import Encounter
from models.Patient import Patient
from models.Organisation import Organisation
from models.Procedure import Procedure
from models.Observation import Observation

from Utils import getConnection
from Utils import convertIdFromOmopToFhir
from Utils import get, delete


def loadLocations(con):
    locationsQuery = '''select distinct careunit from mimiciv.transfers where careunit is not null'''
    locationsDf = pd.read_sql_query(locationsQuery, con)
    for _, row in locationsDf.iterrows():
        location = Location(str(uuid.uuid4()), row.careunit)
        location.postToFhir()


def loadEncounters(con):
    encountersQuery = '''select
    vo.visit_occurrence_id as id,
    (
        case when vo.admitting_source_concept_id is null then 'outpatient' else 
        (
            case when vo.admitting_source_concept_id = 0 then 'outpatient' else 'inpatient' end
        ) end
    ) as code,
    vo.person_id as person_id,
    vo.visit_start_datetime as visit_start_datetime,
    vo.visit_end_datetime as visit_end_datetime
    from
    omop_test_20220817.visit_occurrence vo
    ;
    '''
    encountersDf = pd.read_sql_query(encountersQuery, con)
    for i, row in encountersDf.iterrows():
        if ((i % 1000) == 0):
            print('i: ', i)
        fhirId = convertIdFromOmopToFhir(row.id)
        fhirPersonId = convertIdFromOmopToFhir(row.person_id)
        encounter = Encounter(
            id=fhirId,
            code=row.code,
            person_id=fhirPersonId,
            visit_end_datetime = row.visit_end_datetime,
            visit_start_datetime = row.visit_start_datetime,
            location_list = [],
            )
    encounter.postToFhir()


def loadPatients(con):
    patientsQuery = '''select
    per.person_id as id,
    lower(con.concept_name) as gender
    from
    omop_test_20220817.person per
    inner join omop_test_20220817.concept con
    on con.concept_id = per.gender_concept_id
    ;
    '''
    print('Getting the data from DB')
    patientsDf = pd.read_sql_query(patientsQuery, con)
    print('Putting the data to FHIR')
    for i, row in patientsDf.iterrows():
        if ((i % 1000) == 0):
            print('i: ', i)
        fhirId = convertIdFromOmopToFhir(row.id) # 'm' + str(row.id)[1:] if str(row.id).startswith('-') else 'p' + str(row.id)
        patient = Patient(id=fhirId, gender=str(row.gender))
        patient.postToFhir()


def loadProcedures(con):
    proceduresQuery = '''select
    po.procedure_occurrence_id as id,
    po.procedure_datetime as procedure_datetime,
    con.concept_code as concept_code,
    con.concept_name as concept_name,
    po.person_id as person_id
    from
    omop_test_20220817.procedure_occurrence po
    inner join omop_test_20220817.concept con
    on con.concept_id = po.procedure_concept_id
    where con.vocabulary_id = 'SNOMED'
    ;
    '''
    print('Getting the data from DB')
    proceduresDf = pd.read_sql_query(proceduresQuery, con)
    print('Putting the data to FHIR')
    for i, row in proceduresDf.iterrows():
        if ((i % 1000) == 0):
            print('i: ', i)
        fhirId = convertIdFromOmopToFhir(row.id)
        procedure = Procedure(
            id=fhirId,
            procedure_datetime=row.procedure_datetime,
            concept_code=row.procedure_datetime,
            concept_name=row.concept_name,
            patient_id=row.patient_id
            )
        procedure.postToFhir()


def loadObservation(con):
    observationQuery = '''select
    obs.observation_id as id,
    con.concept_id as concept_id,
    con.concept_name as concept_name,
    obs.person_id as person_id,
    obs.visit_occurrence_id as visit_occurrence_id,
    obs.observation_datetime as observation_datetime,
    obs.value_as_number as value_as_number,
    obs.*
    from
    omop_test_20220817.observation obs
    inner join omop_test_20220817.concept con
    on con.concept_id = obs.observation_concept_id
    where con.vocabulary_id = 'LOINC'
    ;
    '''
    print('Getting the data from DB')
    observationDf = pd.read_sql_query(observationQuery, con)
    print('Putting the data to FHIR')
    for i, row in observationDf.iterrows():
        if ((i % 1000) == 0):
            print('i: ', i)
        fhirId = convertIdFromOmopToFhir(row.id)
        observation = Observation(
            id=fhirId,
            concept_id=row.concept_id,
            concept_name=row.concept_name,
            patient_id=row.patient_id,
            encounter_id=row.encounter_id,
            observation_datetime=row.observation_datetime,
            value_as_number=row.value_as_number
        )
        observation.postToFhir()


def deleteAllPatients():
    url = 'http://superbugai.erc.monash.edu:8082/fhir/Patient?organization=2&_count=100'
    nextLink = url
    while True:
        response = get(url=nextLink)
        responseJson = json.loads(response.text)
        entries = responseJson['entry']
        for entry in entries:
            id = entry['resource']['id']
            print('id: ', id)
            response = delete('http://superbugai.erc.monash.edu:8082/fhir/Patient/' + id + '?hardDelete=true')
            print('response: ', response)
        links = responseJson['link']
        for link in links:
            if link['relation'] == 'next':
                nextLink = link['url']
        if not nextLink:
            break
        print('featching records from nextLink: ', nextLink)


def loadOrganisation():
    organisation = Organisation()
    organisation.postToFhir()


def loadAllResources(con):
    # loadOrganisation()
    # loadLocations(con=con)
    loadPatients(con=con)
    # loadEncounters(con=con)
    # loadProcedures(con=con)
    # loadObservation(con=con)


if __name__ == "__main__":

    con = getConnection()
    loadAllResources(con=con)
    # deleteAllPatients()
