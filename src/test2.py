import random

from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference


if __name__ == '__main__':

    import psycopg2
    import pandas as pd

    con = psycopg2.connect(
        dbname='mimic4',
        user='postgres',
        host='superbugai.erc.monash.edu',
        port=5434,
        password='mysecretpassword'
    )

    diagnosisQuery = '''select
        distinct
        con_ocu.person_id,
        con_ocu.visit_occurrence_id,
        con_ocu.condition_occurrence_id,
        con_ocu.condition_concept_id,
        con.concept_name,
        con_ocu.condition_start_datetime,
        mic.spec_itemid,
        mic.spec_type_desc
        from
        omop_test_20230809.condition_occurrence con_ocu
        inner join omop_test_20230809.concept con
        on con.concept_id = con_ocu.condition_concept_id
        inner join omop_migration_etl_20230809.cdm_condition_occurrence cdm_con_ocu
        on con_ocu.condition_occurrence_id = cdm_con_ocu.condition_occurrence_id
        left join mimiciv.microbiologyevents mic
        on (cdm_con_ocu.trace_id::jsonb -> 'hadm_id') = mic.hadm_id::text::jsonb
        and
        (
            (mic.charttime between con_ocu.condition_start_datetime and con_ocu.condition_end_datetime)
            or
            (mic.storetime between con_ocu.condition_start_datetime and con_ocu.condition_end_datetime)
        )
        and mic.charttime = (
            select
            max(mic_max.charttime)
            from
            mimiciv.microbiologyevents mic_max
            where mic_max.hadm_id = mic.hadm_id
            and
            (
                (mic_max.charttime between con_ocu.condition_start_datetime and con_ocu.condition_end_datetime)
                or
                (mic_max.storetime between con_ocu.condition_start_datetime and con_ocu.condition_end_datetime)
            )
        )
        where con.concept_name like '%Seps%'
        and mic.spec_itemid is not null and mic.spec_type_desc is not null
        limit 50
        ;
        '''

    diagnosisDf = pd.read_sql_query(diagnosisQuery, con)

    for i, row in diagnosisDf.iterrows():
        entities = []
        print('Person ID: ', row.person_id, 'Visit Occurrence ID: ', row.visit_occurrence_id, 'Condition Occurrence ID: ', row.condition_occurrence_id)

        # print('row.charttime: ', row.condition_start_datetime)
        # print(str(random.randint(2008, 2019)) + str(random.randint(1, 12)) + str(random.randint(1, 30)) + ' ' + str(row.condition_start_datetime).split(' ')[1])
        # print(type(row.condition_start_datetime))
        ts = row.condition_start_datetime
        # print(pd.Timestamp(year=random.randint(2008, 2019)), month=ts.month, day=ts.day, hour=ts.hour, minute=ts.minute, second=ts.second)
        # row.condition_start_datetime.year = random.randint(2008, 2019)
        diagnosticReport = DiagnosticReport(
            id=row.condition_occurrence_id,
            status='final',
            issued=pd.Timestamp(year=random.randint(2008, 2019), month=ts.month, day=ts.day, hour=ts.hour, minute=ts.minute, second=ts.second),
            subject=Reference(reference='Patient/' + str(row.person_id)),
            encounter=Reference(reference='Encounter/' + str(row.visit_occurrence_id)),
            code=CodeableConcept(coding=[Coding(
                system='http://fhir.mimic.mit.edu/StructureDefinition/mimic-observation-micro-test',
                code=row.spec_itemid,
                display=row.spec_type_desc
                )]),
            category=[CodeableConcept(coding=[Coding(
                system='http://terminology.hl7.org/CodeSystem/v2-0074',
                code='MB',
                display='microbiology'
                )])],
            conclusionCode=[CodeableConcept(coding=[Coding(
                system='http://snomed.info/sct',
                code=row.condition_concept_id,
                display=row.concept_name
                )])],
            )

        with open('data/' + str(row.person_id) + '_' + str(row.condition_occurrence_id) + ".json", "w") as outfile:
            outfile.write(diagnosticReport.json())
