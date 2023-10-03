import json

from Utils import post


class Encounter:


    def __init__(self, id, code, person_id, visit_end_datetime, visit_start_datetime, location_list):
        self.id = str(id)
        self.code = str(code)
        self.person_id = str(person_id)
        self.visit_end_datetime = str(visit_end_datetime)
        self.visit_start_datetime = str(visit_start_datetime)
        self.location_list = location_list


    def postToFhir(self):

        with open('src/templates/Encounter.json') as f:
            encounterJsonTemplate = f.read()

        with open('src/templates/LocationListitem.json') as f:
            LocationJsonTemplate = f.read()

        locationJson = ""
        for i in range(len(self.location_list)):
            locationJson += LocationJsonTemplate\
                .replace('{{ id }}', self.location_list[i]['id'])\
                .replace('{{ intime }}', self.location_list[i]['intime'])\
                .replace('{{ outtime }}', self.location_list[i]['outtime'])

        encounterJson = encounterJsonTemplate\
            .replace('{{ id }}', self.id)\
            .replace('{{ code }}', self.code)\
            .replace('{{ patient_id }}', self.person_id)\
            .replace('{{ visit_end_datetime }}', self.visit_end_datetime)\
            .replace('{{ visit_start_datetime }}', self.visit_start_datetime)\
            .replace('{{ locations_list }}', locationJson)

        response = post('Encounter', json.loads(encounterJson))

        # print(str(response)) ## TODO: use logging instead of printing
