import logging
from datetime import datetime

import requests

from communication import RestServer
from communication.api.json_transfer import ReceiveJsonApi
from development_system.development_system_configuration import DevelopmentSystemConfiguration

TESTER_URL = 'http://25.34.53.59:1234'

class DevelopmentSystemCommunicationController:

    def __init__(self, developing_system_configuration: DevelopmentSystemConfiguration,
                 handler, semaphore_handler):

        self.ip_address = developing_system_configuration.ip_address
        self.port = developing_system_configuration.port
        self.execution_system_url = developing_system_configuration.execution_system_url
        self.development_system_controller_handler = handler
        self.semaphore_handler = semaphore_handler

    def handle_message(self, json_record: dict) -> None:

        self.development_system_controller_handler(json_record)
        self.semaphore_handler()

    def start_developing_rest_server(self) -> None:

        server = RestServer()
        server.api.add_resource(ReceiveJsonApi,
                                "/",
                                resource_class_kwargs={
                                    'handler': self.handle_message
                                })
        server.run(host=self.ip_address, port=self.port, debug=False)

    def send_classifier_to_execution_system(self, classifier_path):

        try:
            with open(classifier_path, 'rb') as file_to_send:
                response = requests.post(self.execution_system_url, files={'file': file_to_send})
            if not response.ok:
                logging.error("Failed to send the classifier to the execution system")
            else:
                print("Best Classifier sent to the execution system")
        except requests.exceptions.RequestException as ex:
            logging.error("Error during the send of the classifier: %s", ex)

def send_to_testing_system(scenario):

    print(f"Sending scenario: {scenario} to testing system")
    timestamp = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S.%f")
    # Create a dictionary with requested data
    dictionary = {
        'scenario_id': scenario,
        'timestamp': timestamp
    }
    # Send data
    try:
        response = requests.post(TESTER_URL, json=dictionary)
        if not response.ok:
            logging.error("Failed to send raw dataset")
    except requests.exceptions.RequestException as ex:
        logging.error(f"Unable to send scenario msg to testing system.\tException %{ex}\n")
