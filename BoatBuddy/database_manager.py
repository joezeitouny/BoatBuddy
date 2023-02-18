import json
import threading
import uuid
from enum import Enum
from queue import Queue

import boto3

from BoatBuddy import utils, config


class DatabaseManagerStatus(Enum):
    STARTING = 1
    OFFLINE = 2
    ONLINE = 4


class DatabaseManagerItemType(Enum):
    SNAPSHOT = 1
    SESSION_SNAPSHOT = 2
    SESSION_SUMMARY = 3


class DatabaseManager:

    def __init__(self, options):
        self._options = options
        self._exit_signal = threading.Event()
        self._status = DatabaseManagerStatus.STARTING
        self._buffer = Queue()

        if not self._options.db_storage:
            return

        # Set up the default session with the provided credentials
        boto3.setup_default_session(aws_access_key_id=self._options.db_access_key,
                                    aws_secret_access_key=self._options.db_secret_key, region_name='eu-west-3')
        try:
            self._db_resource = boto3.resource('dynamodb')
            self._db_client = boto3.client('dynamodb')
            self._initialize_schema_thread = threading.Thread(target=self._initialize_schema)
            self._initialize_schema_thread.start()
            self._main_loop_thread = threading.Thread(target=self._main_loop)
            self._main_loop_thread.start()
        except Exception as e:
            utils.get_logger().error(f'Could not initialize data storage. Details: {e}')
            self._status = DatabaseManagerStatus.OFFLINE

    def _initialize_schema(self):
        if self._schema_exists():
            self._status = DatabaseManagerStatus.ONLINE
            return

        self._create_table(config.DB_TABLE_APPLICATION, config.DB_TABLE_APPLICATION_SCHEMA,
                           config.DB_TABLE_APPLICATION_ATTRIBUTE_DEFINITIONS)

        self._create_table(config.DB_TABLE_OTHER_SNAPSHOTS, config.DB_TABLE_OTHER_SNAPSHOTS_SCHEMA,
                           config.DB_TABLE_OTHER_SNAPSHOTS_ATTRIBUTE_DEFINITION)

        self._create_table(config.DB_TABLE_SESSION_SNAPSHOTS, config.DB_TABLE_SESSION_SNAPSHOTS_SCHEMA,
                           config.DB_TABLE_SESSION_SNAPSHOTS_ATTRIBUTE_DEFINITION)

        self._create_table(config.DB_TABLE_SESSION_SUMMARY, config.DB_TABLE_SESSION_SUMMARY_SCHEMA,
                           config.DB_TABLE_SESSION_SUMMARY_ATTRIBUTE_DEFINITION)

        self._status = DatabaseManagerStatus.ONLINE

    def _schema_exists(self) -> bool:
        try:
            # Query for the application table
            self._db_client.describe_table(TableName=f'{config.DB_TABLE_NAME_PREFIX}{config.DB_TABLE_APPLICATION}')
            return True
        except Exception as e:
            utils.get_logger().debug(f'Schema already exists. Details {e}')
            return False

    def _create_table(self, table_name, key_schema, attribute_definitions):
        table = self._db_resource.create_table(
            TableName=config.DB_TABLE_NAME_PREFIX + table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput={
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5}
        )
        table.wait_until_exists()

    def _main_loop(self):
        while not self._exit_signal.is_set():
            if self._status != DatabaseManagerStatus.ONLINE:
                continue

            # If the buffer is empty then skip this iteration
            if self._buffer.qsize() == 0:
                continue

            buffer_item = self._buffer.get()
            if buffer_item['type'] == DatabaseManagerItemType.SNAPSHOT.value:
                self._add_item(config.DB_TABLE_OTHER_SNAPSHOTS, buffer_item['payload'])
            elif buffer_item['type'] == DatabaseManagerItemType.SESSION_SNAPSHOT.value:
                self._add_item(config.DB_TABLE_SESSION_SNAPSHOTS, buffer_item['payload'])
            elif buffer_item['type'] == DatabaseManagerItemType.SESSION_SUMMARY.value:
                self._add_item(config.DB_TABLE_SESSION_SUMMARY, buffer_item['payload'])

    def _add_item(self, table_name, payload):
        try:
            self._db_client.put_item(TableName=f'{config.DB_TABLE_NAME_PREFIX}{table_name}', Item=payload)
        except Exception as e:
            utils.get_logger().debug(f'Could not update item in table \'{table_name}\'. Details: {e}')

    def finalize(self):
        self._exit_signal.set()

    def add_snapshot(self, columns, payload):
        random_id = str(uuid.uuid4())
        utils.get_logger().debug(random_id)
        payload.update({'guid': random_id})

        buffer_item = {'type': DatabaseManagerItemType.SNAPSHOT.value, 'payload': payload}

        self._buffer.put(buffer_item)

    def add_session_snapshot(self, session_id, metadata_headers, metadata_values):
        payload = {}
        counter = 0

        while counter < len(metadata_headers):
            payload.update({f"{metadata_headers[counter]}": {"S": f"{metadata_values[counter]}"}})
            counter += 1

        payload.update({"session_id": {"S": f"{session_id}"}})
        payload_json = json.dumps(payload)

        buffer_item = {'type': DatabaseManagerItemType.SESSION_SNAPSHOT.value, 'payload': payload}

        self._buffer.put(buffer_item)

    def add_session_summary(self, session_id, columns, payload):
        payload.update({'session_id': session_id})

        buffer_item = {'type': DatabaseManagerItemType.SESSION_SUMMARY.value, 'payload': payload}

        self._buffer.put(buffer_item)
