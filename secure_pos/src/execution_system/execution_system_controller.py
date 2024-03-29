import os.path

import pandas as pd

from execution_system.execution_system_configuration import ExecutionSystemConfiguration
from execution_system.communication_controller import CommunicationController, CLASSIFIER_MODEL_PATH
from execution_system.communication_controller import send_testing_timestamp
from execution_system.system_mode_tracker import SystemModeTracker
from execution_system.classifier_model_deployment import ClassifierModelDeployment
from execution_system.attack_risk_classifier import AttackRiskClassifier
from utility import data_folder

CONFIGURATION_FILE = 'execution_system/execution_config.json'
CONFIGURATION_SCHEMA = 'execution_system/execution_config_schema.json'
TESTING_MODE = False


class ExecutionSystemController:
    """
    Class responsible for executing the main logic workflow of the execution system.

    - It configures the system and all the necessary resources.
    - It handles the reception and the deployment of a classifier model.
    - It handles the reception ànd the classification of a new session.
    """

    def __init__(self):
        self.__configuration = ExecutionSystemConfiguration(CONFIGURATION_FILE, CONFIGURATION_SCHEMA)
        self.__communication_controller = \
            CommunicationController(self.__configuration,
                                    self.handle_new_prepared_session_reception,
                                    self.handle_classifier_model_deployment)
        self.__system_mode_tracker = SystemModeTracker(self.__configuration)
        self.__deployed_classifier_model = ClassifierModelDeployment()

    def run(self) -> None:
        """ Start REST server of the Execution system """
        self.__communication_controller.start_execution_rest_server()

    def handle_classifier_model_deployment(self) -> None:
        """
        Handle the deployment of a new classifier model
        whenever it is received by the REST endpoint.
        """
        # Start classifier
        self.__deployed_classifier_model.load_classifier_model()
        self.__system_mode_tracker.development_mode = False

        # send timestamp for testing
        if TESTING_MODE:
            send_testing_timestamp(scenario_id=4)

    def handle_new_prepared_session_reception(self, json_session: dict) -> None:
        """
        Handle a new session whenever it is received by the REST endpoint.
        :param json_session: received JSON data
        """
        if os.path.exists(os.path.join(data_folder, CLASSIFIER_MODEL_PATH)) \
                and self.__system_mode_tracker.development_mode:
            self.handle_classifier_model_deployment()

        if self.__system_mode_tracker.development_mode:
            return

        # Get prepared session
        session_id = json_session['id'][0]
        prepared_session = pd.DataFrame(data=json_session)
        prepared_session = prepared_session.iloc[:, 1:-2]

        # Classify session
        attack_risk_classifier = \
            AttackRiskClassifier(self.__deployed_classifier_model.get_classifier_model(),
                                 session_id, prepared_session)
        session_risk_level = attack_risk_classifier.provide_attack_risk_level()

        # Send label to monitoring system
        print("session classified")
        if self.__system_mode_tracker.is_session_in_monitoring_window():
            self.__communication_controller.send_attack_risk_label(
                attack_risk_classifier.attack_risk_label_converter()
            )

        if session_risk_level == '1':
            print("Attack detected")

        if TESTING_MODE:
            send_testing_timestamp(scenario_id=5, session_id=session_id)
