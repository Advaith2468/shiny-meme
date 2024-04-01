import threading
import json
from datetime import datetime
from queue import Queue
import socket
from netcore_server import TcpSession
from PolygonStats.Configuration import ConfigurationManager as PolyConfig
from PolygonStats.RawWebhook import RawWebhookManager
from PolygonStats.Models import Session, Account, LogEntry, Stats
import logging

logging.basicConfig(level=logging.DEBUG)

class ClientSession(TcpSession):
    def __init__(self, server):
        super().__init__(server)
        self.message_buffer = ""
        self.account_name = None
        self.db_manager = MySQLConnectionManager()
        self.db_session_id = -1
        self.account_id = None
        self.message_count = 0
        self.logger = None
        self.last_message_datetime = datetime.utcnow()
        self.last_encounter_pokemon = None
        self.holo_pokemon = {}

    def is_connected(self):
        return (datetime.utcnow() - self.last_message_datetime).total_seconds() <= 1200

    def on_connected(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8192 * 4)
        self.socket.settimeout(10)

    def on_disconnected(self):
        logging.info(f"User {self.account_name} with sessionId {self.id} has disconnected.")
        if PolyConfig.Shared.Config.MySql.Enabled and self.db_session_id != -1:
            with self.db_manager.get_context() as context:
                db_session = self.db_manager.get_session(context, self.db_session_id)
                db_session.end_time = self.last_message_datetime
                context.save_changes()

    def on_received(self, buffer):
        self.last_message_datetime = datetime.utcnow()
        current_message = buffer.decode('utf-8')

        if PolyConfig.Shared.Config.Debug.DebugMessages:
            logging.debug(f"Message #{self.message_count} was received!")

        self.message_buffer += current_message
        json_strings = self.message_buffer.split("\n")
        self.message_buffer = ""

        if PolyConfig.Shared.Config.Debug.DebugMessages:
            logging.debug(f"Message was split into {len(json_strings)} jsonObjects.")

        for index, json_string in enumerate(json_strings):
            trimmed_json_string = json_string.strip("\r\n")

            if not trimmed_json_string.startswith("{"):
                if PolyConfig.Shared.Config.Debug.DebugMessages:
                    logging.debug("Json string didn't start with a {.")
                continue

            if not trimmed_json_string.endswith("}"):
                if PolyConfig.Shared.Config.Debug.DebugMessages:
                    logging.debug("Json string didn't end with a }.")
                if index == len(json_strings) - 1:
                    self.message_buffer = json_string
                continue

            try:
                message = json.loads(trimmed_json_string)
                if PolyConfig.Shared.Config.Debug.DebugMessages:
                    logging.debug(f"Handle JsonObject #{index} with {len(message['payloads'])} payloads.")

                for payload in message['payloads']:
                    if payload['account_name'] is None or payload['account_name'] == "null":
                        continue
                    self.add_account_and_session_if_needed(payload)
                    self.handle_payload(payload)
                    if PolyConfig.Shared.Config.RawData.Enabled:
                        RawWebhookManager.shared.add_raw_data({
                            "origin": payload['account_name'],
                            "rawData": {
                                "type": payload['type'],
                                "lat": payload['lat'],
                                "lng": payload['lng'],
                                "timestamp": payload['timestamp'],
                                "raw": True,
                                "payload": payload['proto']
                            }
                        })
            except json.JSONDecodeError:
                if index == len(json_strings) - 1:
                    self.message_buffer = json_string

        if PolyConfig.Shared.Config.Debug.DebugMessages:
            logging.debug(f"Message #{self.message_count} was handled!")

    def on_error(self, error):
        logging.error(f"Chat TCP session caught an error with code {error}")

    def add_account_and_session_if_needed(self, payload):
        if self.account_name != payload['account_name']:
            self.account_name = payload['account_name']
            self.get_stat_entry()

            if PolyConfig.Shared.Config.MySql.Enabled:
                with self.db_manager.get_context() as context:
                    account = context.Accounts.where(lambda a: a.Name == self.account_name).first_or_default()
                    if account is None:
                        account = Account(Name=self.account_name, HashedName="")
                        context.Accounts.add(account)
                    logging.info(f"User {self.account_name} with sessionId {self.id} has connected.")
                    db_session = Session(StartTime=datetime.utcnow())
                    account.Sessions.append(db_session)
                    context.save_changes()
                    self.db_session_id = db_session.Id
                    self.account_id = account.Id

    def get_stat_entry(self):
        if PolyConfig.Shared.Config.Http.Enabled:
            return StatManager.sharedInstance.get_entry(self.account_name)
        return None

    def handle_payload(self, payload):
        self.logger.debug(f"Payload with type {payload.get_method_type():g}")
        method_type = payload.get_method_type()
        if method_type == AllResquestTypesProto.RequestTypeMethod.Encounter:
            encounter_proto = EncounterOutProto.ParseFromString(payload['bytes'])
            self.logger.debug(f"Proto: {json.dumps(encounter_proto)}")
            self.process_encounter(payload['account_name'], encounter_proto, payload)
        elif method_type == AllResquestTypesProto.RequestTypeMethod.CatchPokemon:
            caught_pokemon = CatchPokemonOutProto.ParseFromString(payload['bytes'])
            self.logger.debug(f"Proto: {json.dumps(caught_pokemon)}")
            self.process_caught_pokemon(caught_pokemon)
        # Implement other method types handling similarly
