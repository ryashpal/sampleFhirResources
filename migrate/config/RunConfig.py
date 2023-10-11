import json
from migrate.Utils import get
from migrate.Utils import getConnection


def createLocationLookup():
    print('getting connection')
    con = getConnection()

    print('creating table')
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS omop_test_20220817.location_id_map (id varchar, name varchar);")
    cur.close()

    print('fetching data')
    url = 'http://superbugai.erc.monash.edu:8082/fhir/Location?organization=T001&_count=50'
    response = get(url=url)
    responseJson = json.loads(response.text)
    entries = responseJson['entry']
    for entry in entries:
        id = entry['resource']['id']
        name = entry['resource']['name']
        print('inserting id: ', str(id), ' name: ', str(name))
        cur = con.cursor()
        cur.execute('INSERT INTO omop_test_20220817.location_id_map (id, name) VALUES (%s, %s)', (id, name))
        cur.close()
    print('completed loading the data')
    con.commit()
    con.close()


run_config = [
    {
        'entity': 'Organization',
        'type': 'migrate',
        'sqlFilePath': 'migrate/sql/select/Organization.sql',
        'xmlTemplatePath': 'migrate/templates/Organization.json',
        'xml_sql_mapping': {
            'id': 'id',
            'name': 'organization_name',
        }
    },
    {
        'entity': 'Location',
        'type': 'migrate',
        'sqlFilePath': 'migrate/sql/select/Transfer.sql',
        'xmlTemplatePath': 'migrate/templates/Location.json',
        'xml_sql_mapping': {
            'id': 'id',
            'name': 'careunit',
        }
    },
    {
        'entity': 'Patient',
        'type': 'migrate',
        'sqlFilePath': 'migrate/sql/select/Person.sql',
        'xmlTemplatePath': 'migrate/templates/Patient.json',
        'xml_sql_mapping': {
            'id': 'id',
            'gender': 'gender',
        }
    },
    {
        'type': 'execute',
        'function': createLocationLookup
    },
    {
        'entity': 'Encounter',
        'type': 'migrate',
        'sqlFilePath': 'migrate/sql/select/VisitOccurrence.sql',
        'xmlTemplatePath': 'migrate/templates/Encounter.json',
        'xml_sql_mapping': {
            'id': 'id',
            'class||code': 'code',
            'subject||reference': 'person_id',
            'participant||period||end': 'visit_end_datetime',
            'participant||period||start': 'visit_start_datetime',
            'location': {
                'sqlFilePath': 'migrate/sql/select/LocationListitem.sql',
                'xmlTemplatePath': 'migrate/templates/LocationListitem.json',
                'xml_sql_mapping': {
                    'location||reference': 'id',
                    'period||start': 'intime',
                    'period||end': 'outtime',
                }
            }
        }
    },
    {
        'entity': 'Observation',
        'type': 'migrate',
        'sqlFilePath': 'migrate/sql/select/Measurement.sql',
        'xmlTemplatePath': 'migrate/templates/Observation.json',
        'xml_sql_mapping': {
            'id': 'id',
            'code||coding||code': 'measurement_concept_id',
            'code||coding||display': 'measurement_concept_name',
            'code||text': 'measurement_concept_name',
            'subject||reference': 'person_id',
            'encounter||reference': 'visit_occurrence_id',
            'effectiveDateTime': 'measurement_datetime',
            'valueQuantity||value': 'value_as_number',
            'valueQuantity||unit': 'unit_concept_id',
            'valueQuantity||code': 'unit_concept_code',
        }
    },
]
