import json

from Utils import put


class Patient:


    def __init__(self, id, gender):
        self.id = id
        self.gender = gender


    def postToFhir(self):

        with open('src/templates/Patient.json') as f:
            patientJsonTemplate = f.read()

        patientJson = patientJsonTemplate\
            .replace('{{ id }}', self.id)\
            .replace('{{ gender }}', self.gender)

        response = put('Patient/' + str(self.id), json.loads(patientJson))

        # print(response.text) ## TODO: use logging instead of printing
