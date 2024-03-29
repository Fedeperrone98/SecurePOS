"""
This module contains API classes which handle json reception and sending.
In order to use the API, add them as resources to your Flask application.
"""
from typing import Callable

from flask import request
from flask_restful import Resource

from utility.json_validation import validate_json_data_file


class ReceiveJsonApi(Resource):
    """
    This API allows other nodes to send json to the Flask application.
    """
    
    def __init__(self,
                 json_schema_path: str = None,
                 handler: Callable[[dict], None] = None):
        """
        Initialize the API.
        :param json_schema_path
        :param handler: optional function to call after the json has been saved in the filesystem.
                        The handler function should not take too much time to return
                        (start a new thread, if necessary).
        """

        self.json_schema_path = json_schema_path
        self.handle_request = handler
    
    def post(self):
        """
        Handle a POST request.
        Other nodes should send a POST request when they want to send a json to this endpoint.
        The json must be inserted in the ``json['json_file']`` field of the request.
        :return: status code 201 on success, 400 if the file does not exist
        """
        received_json = request.get_json()
        
        # Validate received json
        if self.json_schema_path is not None \
                and not validate_json_data_file(received_json, self.json_schema_path):
            return 'JSON validation failed', 400
        
        # Execute the handler function if it was specified
        if self.handle_request is not None:
            self.handle_request(received_json)
        
        return 'JSON correctly received', 201
