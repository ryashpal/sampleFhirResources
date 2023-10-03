from fhir.resources.bundle import Bundle
from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.bundle import BundleEntry
from fhir.resources.identifier import Identifier
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from fhir.resources.observation import Observation
from fhir.resources.quantity import Quantity


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

    diagnosticReportsQuery = '''select distinct subject_id, micro_specimen_id, spec_type_desc, spec_itemid, charttime from mimiciv.microbiologyevents limit 50;'''
    diagnosticReportsDf = pd.read_sql_query(diagnosticReportsQuery, con)
    for i, row in diagnosticReportsDf.iterrows():
        entities = []
        print('subject id: ', row.subject_id, 'micro specimen id: ', row.micro_specimen_id)

        diagnosticReport = DiagnosticReport(
            id='microbiology-investigation',
            status='final',
            identifier=[Identifier(system='Micro Specimen ID', value=row.micro_specimen_id)],
            category=[CodeableConcept(coding=[Coding(system='Specimen Type Description', code=row.spec_type_desc)])],
            code=CodeableConcept(coding=[Coding(system='Specimen Type ID', code=row.spec_itemid)]),
            subject=Reference(identifier=Identifier(system='Patient/ID', value=row.subject_id)),
            issued=row.charttime,
            )
        diagnosticReportBundleEntry = BundleEntry(fullUrl='https://example.com/base/DiagnosticReport/micro', resource_type='BundleEntry', resource=diagnosticReport)
        entities.append(diagnosticReportBundleEntry)

        organismQuery = '''select distinct subject_id, org_itemid, org_name from mimiciv.microbiologyevents where subject_id = ''' + str(row.subject_id) + ''' and micro_specimen_id = ''' + str(row.micro_specimen_id)
        organismDf = pd.read_sql_query(organismQuery, con)
        for j, organismRow in organismDf.iterrows():
            observationOrg = Observation(
                id='organism',
                identifier=[Identifier(system='Organism Item ID', value=organismRow.org_itemid)],
                status='final',
                code=CodeableConcept(coding=[Coding(code='ORGANISM')]),
                subject=Reference(identifier=Identifier(system='Patient/ID', value=organismRow.subject_id)),
                valueCodeableConcept=CodeableConcept(coding=[Coding(code=organismRow.org_name)]),
                )
            OrganismBundleEntry = BundleEntry(fullUrl='https://example.com/base/Observation', resource_type='BundleEntry', resource=observationOrg)
            entities.append(OrganismBundleEntry)

            if organismRow.org_itemid and str(organismRow.org_itemid) != 'nan':
                antibioticQuery = '''select distinct subject_id, ab_itemid, ab_name, dilution_comparison, dilution_value, interpretation from mimiciv.microbiologyevents where subject_id = ''' + str(row.subject_id) + ''' and micro_specimen_id = ''' + str(row.micro_specimen_id) + ''' and org_itemid = ''' + str(organismRow.org_itemid)
                antibioticDf = pd.read_sql_query(antibioticQuery, con)
                for z, antibioticRow in antibioticDf.iterrows():
                    observationAnt = Observation(
                    id='antibiotic',
                    identifier=[Identifier(system='Antibiotic Item ID', value=antibioticRow.ab_itemid)],
                    status='final',
                    code=CodeableConcept(coding=[Coding(code=antibioticRow.ab_name)]),
                    subject=Reference(identifier=Identifier(system='Patient/ID', value=antibioticRow.subject_id)),
                    valueQuantity=Quantity(value=antibioticRow.dilution_value, comparator=str(antibioticRow.dilution_comparison).strip()),
                    interpretation=[CodeableConcept(coding=[Coding(system='http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation', code=antibioticRow.interpretation)])],
                    )
                    AntibioticBundleEntry = BundleEntry(fullUrl='https://example.com/base/Observation', resource_type='BundleEntry', resource=observationAnt)
                    entities.append(AntibioticBundleEntry)

        bundle = Bundle(id='micro', type='collection', entry=entities)
        with open('data/' + str(row.subject_id) + '_' + str(row.micro_specimen_id) + ".json", "w") as outfile:
            outfile.write(bundle.json())
