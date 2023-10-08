import json

from Utils import put


class Procedure:


    def __init__(self, id, procedure_datetime, concept_code, concept_name, patient_id, encounter_id):
        self.id = id
        self.procedure_datetime = procedure_datetime
        self.concept_code = concept_code
        self.concept_name = concept_name
        self.patient_id = patient_id
        self.encounter_id = encounter_id


    def postToFhir(self):

        with open('src/templates/Procedure.json') as f:
            procedureJsonTemplate = f.read()

        procedureJson = procedureJsonTemplate\
            .replace('{{ id }}', self.id)\
            .replace('{{ procedure_datetime }}', str(self.procedure_datetime))\
            .replace('{{ concept_code }}', self.concept_code)\
            .replace('{{ concept_name }}', self.concept_name)\
            .replace('{{ patient_id }}', self.patient_id)\
            .replace('{{ encounter_id }}', self.encounter_id)

        # print('procedureJson: ', procedureJson)
        response = put('Procedure/' + str(self.id), json.loads(procedureJson))

        # print(response.text) ## TODO: use logging instead of printing
