import json

from Utils import put


class DiagnosticReport:


    def __init__(self, id, patient_id, encounter_id, condition_start_datetime, condition_code, condition_name):
        self.id = id
        self.patient_id = patient_id
        self.encounter_id = encounter_id
        self.condition_start_datetime = condition_start_datetime
        self.condition_code = condition_code
        self.condition_name = condition_name


    def postToFhir(self):

        with open('src/templates/DiagnosticReport.json') as f:
            diagnosticReportJsonTemplate = f.read()

        diagnosticReportJson = diagnosticReportJsonTemplate\
            .replace('{{ id }}', self.id)\
            .replace('{{ patient_id }}', self.patient_id)\
            .replace('{{ encounter_id }}', self.encounter_id)\
            .replace('{{ condition_start_datetime }}', self.condition_start_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f'))\
            .replace('{{ condition_code }}', str(self.condition_code))\
            .replace('{{ condition_name }}', self.condition_name)\

        # print('diagnosticReportJson: ', diagnosticReportJson)
        response = put('DiagnosticReport/' + str(self.id), json.loads(diagnosticReportJson))

        # print(response) ## TODO: use logging instead of printing
