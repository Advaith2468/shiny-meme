import base64
from enum import Enum

# Assuming you have the necessary proto definitions for AllTypesAndMessagesResponsesProto.Types
from POGOProtos.Rpc.AllTypesAndMessagesResponsesProto.Types import AllResquestTypesProto

class Payload:
    def __init__(self):
        self.type = 0
        self.proto = ""
        self.lat = 0.0
        self.lng = 0.0
        self.timestamp = 0
        self.token = ""
        self.level = ""
        self.account_name = ""
        self.account_id = ""

    def get_bytes(self):
        return base64.b64decode(self.proto)

    def get_method_type(self):
        return AllResquestTypesProto(self.type)


class MessageObject:
    def __init__(self):
        self.payloads = []
        self.key = ""
