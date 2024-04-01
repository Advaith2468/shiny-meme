class RawData:
    def __init__(self, type, timestamp, lat, lng, raw, payload):
        self.type = type
        self.timestamp = timestamp
        self.lat = lat
        self.lng = lng
        self.raw = raw
        self.payload = payload

class RawDataMessage:
    def __init__(self, origin, rawData):
        self.origin = origin
        self.rawData = rawData
