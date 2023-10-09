import uuid
import json

import pandas as pd

from models.Location import Location
from models.Encounter import Encounter
from models.Patient import Patient
from models.Organisation import Organisation
from models.Procedure import Procedure
from models.Observation import Observation
from models.DiagnosticReport import DiagnosticReport

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
    locationDict = {'Cardiac Surgery': '2', 'Cardiology Surgery Intermediate': '3', 'Surgery/Pancreatic/Biliary/Bariatric': '4', 'Emergency Department': '5', 'Surgical Intensive Care Unit (SICU)': '6', 'Cardiology': '7', 'Labor & Delivery': '8', 'Vascular': '9', 'Obstetrics Postpartum': '10', 'Medicine/Cardiology': '11', 'Medical/Surgical Intensive Care Unit (MICU/SICU)': '12', 'Med/Surg': '13', 'Unknown': '14', 'Coronary Care Unit (CCU)': '15', 'Special Care Nursery (SCN)': '16', 'Medicine/Cardiology Intermediate': '17', 'Neonatal Intensive Care Unit (NICU)': '18', 'Cardiac Vascular Intensive Care Unit (CVICU)': '19', 'Obstetrics (Postpartum & Antepartum)': '20', 'Med/Surg/GYN': '21', 'Trauma SICU (TSICU)': '22', 'Observation': '23', 'Neurology': '24', 'Emergency Department Observation': '25', 'Medicine': '26', 'Hematology/Oncology': '27', 'Surgery/Vascular/Intermediate': '28', 'Neuro Stepdown': '29', 'Thoracic Surgery': '30', 'Obstetrics Antepartum': '31', 'Psychiatry': '32', 'PACU': '33', 'Medical Intensive Care Unit (MICU)': '34', 'Nursery - Well Babies': '35', 'Hematology/Oncology Intermediate': '36', 'Transplant': '37', 'Surgery/Trauma': '38', 'Med/Surg/Trauma': '39', 'Medical/Surgical (Gynecology)': '40', 'Neuro Intermediate': '41', 'Surgery': '42', 'Neuro Surgical Intensive Care Unit (Neuro SICU)': '43'}
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
    inner join omop_test_20220817.micro_cohort coh
    on coh.visit_occurrence_id = vo.visit_occurrence_id
    ;
    '''
    encountersDf = pd.read_sql_query(encountersQuery, con)
    for i, row in encountersDf.iterrows():
        if ((i % 1000) == 0):
            print('i: ', i)
        location_list = []
        transfersQuery = '''select
            trn.careunit,
            trn.intime,
            trn.outtime
            from
            omop_test_20220817.visit_occurrence vo
            inner join mimiciv.admissions adm
            on adm.hadm_id::text = split_part(vo.visit_source_value, '|', 2)
            inner join mimiciv.transfers trn
            on trn.hadm_id = adm.hadm_id
            where vo.visit_occurrence_id=''' + str(row.id) + ''' and trn.careunit is not null
            ;
            '''
        transfersDf = pd.read_sql_query(transfersQuery, con)
        for _, tRow in transfersDf.iterrows():
            transferId = locationDict[tRow.careunit]
            location_list.append({'id': transferId, 'intime': tRow.intime, 'outtime': tRow.outtime})
        fhirId = convertIdFromOmopToFhir(row.id)
        fhirPersonId = convertIdFromOmopToFhir(row.person_id)
        encounter = Encounter(
            id=fhirId,
            code=row.code,
            person_id=fhirPersonId,
            visit_end_datetime = row.visit_end_datetime,
            visit_start_datetime = row.visit_start_datetime,
            location_list = location_list,
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
    inner join omop_test_20220817.micro_cohort coh
    on coh.person_id = per.person_id
    ;
    '''
    print('Getting the data from DB')
    patientsDf = pd.read_sql_query(patientsQuery, con)
    print('Putting the data to FHIR')
    for i, row in patientsDf.iterrows():
        if ((i % 1000) == 0):
            print('i: ', i)
        fhirId = convertIdFromOmopToFhir(row.id)
        patient = Patient(id=fhirId, gender=str(row.gender))
        patient.postToFhir()


def loadProcedures(con):
    proceduresQuery = '''select
    po.procedure_occurrence_id as id,
    po.procedure_datetime as procedure_datetime,
    con.concept_code as concept_code,
    con.concept_name as concept_name,
    po.person_id as person_id,
    po.visit_occurrence_id as visit_occurrence_id
    from
    omop_test_20220817.procedure_occurrence po
    inner join omop_test_20220817.concept con
    on con.concept_id = po.procedure_concept_id
    inner join omop_test_20220817.micro_cohort coh
    on coh.visit_occurrence_id = po.visit_occurrence_id
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
        fhirPatientId = convertIdFromOmopToFhir(row.person_id)
        fhirEncounterId = convertIdFromOmopToFhir(row.visit_occurrence_id)
        procedure = Procedure(
            id=fhirId,
            procedure_datetime=row.procedure_datetime,
            concept_code=row.concept_code,
            concept_name=row.concept_name,
            patient_id=fhirPatientId,
            encounter_id=fhirEncounterId
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
    obs.value_as_number as value_as_number
    from
    omop_test_20220817.observation obs
    inner join omop_test_20220817.concept con
    on con.concept_id = obs.observation_concept_id
    inner join omop_test_20220817.micro_cohort coh
    on coh.visit_occurrence_id = obs.visit_occurrence_id
    where con.vocabulary_id = 'LOINC' and value_as_number <> 'NaN' and value_as_number is not null
    ;
    '''
    print('Getting the data from DB')
    observationDf = pd.read_sql_query(observationQuery, con)
    print('Putting the data to FHIR')
    for i, row in observationDf.iterrows():
        if ((i % 1000) == 0):
            print('i: ', i)
        fhirId = convertIdFromOmopToFhir(row.id)
        fhirPatientId = convertIdFromOmopToFhir(row.person_id)
        fhirEncounterId = convertIdFromOmopToFhir(row.visit_occurrence_id)
        observation = Observation(
            id=fhirId,
            concept_id=row.concept_id,
            concept_name=row.concept_name,
            patient_id=fhirPatientId,
            encounter_id=fhirEncounterId,
            observation_datetime=row.observation_datetime,
            value_as_number=row.value_as_number
        )
        observation.postToFhir()


def loadDiagnosticReport(con):
    diagnosticReportQuery = '''select
    con_ocu.condition_occurrence_id as id,
    con_ocu.visit_occurrence_id,
    con_ocu.person_id,
    con_ocu.condition_concept_id,
    con.concept_name,
    con_ocu.condition_start_datetime
    from
    omop_test_20220817.condition_occurrence con_ocu
    inner join omop_test_20220817.concept con
    on con.concept_id = con_ocu.condition_concept_id
    inner join omop_test_20220817.micro_cohort coh
    on coh.visit_occurrence_id = con_ocu.visit_occurrence_id
    ;
    '''
    print('Getting the data from DB')
    diagnosticReportDf = pd.read_sql_query(diagnosticReportQuery, con)
    print('Putting the data to FHIR')
    for i, row in diagnosticReportDf.iterrows():
        if ((i % 1000) == 0):
            print('i: ', i)
        fhirId = convertIdFromOmopToFhir(row.id)
        fhirPatientId = convertIdFromOmopToFhir(row.person_id)
        fhirEncounterId = convertIdFromOmopToFhir(row.visit_occurrence_id)
        diagnosticReport = DiagnosticReport(
            id=fhirId,
            patient_id=fhirPatientId,
            encounter_id=fhirEncounterId,
            condition_start_datetime=row.condition_start_datetime,
            condition_code=row.condition_concept_id,
            condition_name=row.concept_name
            )
        diagnosticReport.postToFhir()


def deleteAllPatients():
    url = 'http://superbugai.erc.monash.edu:8082/fhir/Patient?organization=2&_count=100'
    while True:
        response = get(url=url)
        responseJson = json.loads(response.text)
        print('responseJson: ', str(responseJson))
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
        print('featching records from url: ', url)


def deleteAllLocations():
    url = 'http://superbugai.erc.monash.edu:8082/fhir/Location?_count=10'
    while True:
        response = get(url=url)
        responseJson = json.loads(response.text)
        print('responseJson: ', str(responseJson))
        entries = responseJson['entry']
        for entry in entries:
            id = entry['resource']['id']
            print('id: ', id)
            response = delete('http://superbugai.erc.monash.edu:8082/fhir/Location/' + id + '?hardDelete=true')
            print('response: ', response)
        links = responseJson['link']
        for link in links:
            if link['relation'] == 'next':
                nextLink = link['url']
        if not nextLink:
            break
        print('featching records from url: ', url)
    # for i in range(1, 43):
    #     print('TRN' + str(i).zfill(3))
    #     response = delete('http://superbugai.erc.monash.edu:8082/fhir/Location/' + ('TRN' + str(i).zfill(3)) + '?hardDelete=true')
    #     print('response: ', response)


def loadOrganisation():
    organisation = Organisation()
    organisation.postToFhir()


def loadAllResources(con):
    # loadOrganisation()
    # loadLocations(con=con)
    # loadPatients(con=con)
    # loadEncounters(con=con)
    loadProcedures(con=con)
    # loadObservation(con=con)
    # loadDiagnosticReport(con=con)


def deleteAllResources():
    # deleteAllPatients()
    deleteAllLocations()


if __name__ == "__main__":

    con = getConnection()
    # loadAllResources(con=con)
    deleteAllResources()
