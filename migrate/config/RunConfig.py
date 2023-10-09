run_config = [
    # {
    #     'entity': 'Organization',
    #     'sqlFilePath': 'migrate/sql/Organization.sql',
    #     'xmlTemplatePath': 'migrate/templates/Organization.json',
    #     'xml_sql_mapping': {
    #         'id': 'id',
    #         'name': 'organization_name',
    #     }
    # },
    # {
    #     'entity': 'Location',
    #     'sqlFilePath': 'migrate/sql/Transfer.sql',
    #     'xmlTemplatePath': 'migrate/templates/Location.json',
    #     'xml_sql_mapping': {
    #         'id': 'id',
    #         'name': 'careunit',
    #     }
    # },
    # {
    #     'entity': 'Patient',
    #     'sqlFilePath': 'migrate/sql/Person.sql',
    #     'xmlTemplatePath': 'migrate/templates/Patient.json',
    #     'xml_sql_mapping': {
    #         'id': 'id',
    #         'gender': 'gender',
    #     }
    # },
    {
        'entity': 'Encounter',
        'sqlFilePath': 'migrate/sql/VisitOccurrence.sql',
        'xmlTemplatePath': 'migrate/templates/Encounter.json',
        'xml_sql_mapping': {
            'id': 'id',
            'class||code': 'code',
            'subject||reference': 'person_id',
            'period||end': 'visit_end_datetime',
            'period||start': 'visit_start_datetime',
            'location': {
                'sqlFilePath': 'migrate/sql/LocationListitem.sql',
                'xmlTemplatePath': 'migrate/templates/LocationListitem.json',
                'xml_sql_mapping': {
                    # 'id': 'id',
                    'period||start': 'intime',
                    'period||end': 'outtime',
                }
            }
        }
    },
]
