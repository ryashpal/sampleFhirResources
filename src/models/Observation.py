import json

from Utils import put


class Observation:


    def __init__(self, id, concept_id, concept_name, patient_id, encounter_id, observation_datetime, value_as_number):
        self.id = id
        self.concept_id = concept_id
        self.concept_name = concept_name
        self.patient_id = patient_id
        self.encounter_id = encounter_id
        self.observation_datetime = observation_datetime
        self.value_as_number = value_as_number


    def postToFhir(self):

        with open('src/templates/Observation.json') as f:
            observationJsonTemplate = f.read()

        observationJson = observationJsonTemplate\
            .replace('{{ id }}', self.id)\
            .replace('{{ concept_id }}', self.concept_id)\
            .replace('{{ concept_name }}', self.concept_name)\
            .replace('{{ patient_id }}', self.patient_id)\
            .replace('{{ encounter_id }}', self.encounter_id)\
            .replace('{{ observation_datetime }}', self.observation_datetime)\
            .replace('{{ value_as_number }}', self.value_as_number)

        response = put('Observation/' + str(self.id), json.loads(observationJson))

        # print(response.text) ## TODO: use logging instead of printing
