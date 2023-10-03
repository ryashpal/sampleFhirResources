import json

from Utils import post


class Organisation:


    def postToFhir(self):

        with open('src/templates/Organization.json') as f:
            organizationJsonTemplate = f.read()

        organizationJson = organizationJsonTemplate

        response = post('Organization', json.loads(organizationJson))

        print(response) ## TODO: use logging instead of printing
