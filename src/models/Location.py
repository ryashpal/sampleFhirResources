import json

from Utils import post


class Location:


    def __init__(self, id, name):
        self.id = id
        self.name = name


    def postToFhir(self):

        with open('src/templates/Location.json') as f:
            locationJsonTemplate = f.read()

        locationJson = locationJsonTemplate\
            .replace('{{ id }}', self.id)\
                .replace('{{ name }}', self.name)

        response = post('Location', json.loads(locationJson))

        print(response) ## TODO: use logging instead of printing
