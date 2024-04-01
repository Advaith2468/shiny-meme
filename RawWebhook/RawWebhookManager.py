import threading
import json
import time
from queue import Queue
import requests
from PolygonStats.Configuration import ConfigurationManager
import logging

logging.basicConfig(level=logging.DEBUG)

class RawWebhookManager:
    _shared = None

    @classmethod
    def shared(cls):
        if not cls._shared:
            cls._shared = RawWebhookManager()
        return cls._shared

    def __init__(self):
        if not ConfigurationManager.Shared.Config.RawData.Enabled:
            return

        self.client = requests.Session()
        self.blocking_raw_data_dict = {}
        self.lock_obj = threading.Lock()
        self.consumer_thread = threading.Thread(target=self.raw_data_consumer)
        self.consumer_thread.start()

    def add_raw_data(self, message):
        if not ConfigurationManager.Shared.Config.RawData.Enabled:
            return

        origin = message['origin']
        raw_data = message['rawData']

        with self.lock_obj:
            if origin not in self.blocking_raw_data_dict:
                self.blocking_raw_data_dict[origin] = Queue()

            self.blocking_raw_data_dict[origin].put(raw_data)

    def raw_data_consumer(self):
        while True:
            for origin, collection in self.blocking_raw_data_dict.items():
                raw_data_list = []
                try:
                    while not collection.empty():
                        raw_data = collection.get_nowait()
                        raw_data_list.append(raw_data)
                except Exception as e:
                    logging.info(f"Error occurred: {e}")

                if raw_data_list:
                    request_data = json.dumps(raw_data_list)
                    headers = {'origin': origin}
                    try:
                        response = self.client.post(ConfigurationManager.Shared.Config.RawData.WebhookUrl, data=request_data, headers=headers)
                        logging.debug(f"Response: {response}")
                    except Exception as e:
                        logging.info(f"Request error: {e}")
                        for data in raw_data_list:
                            collection.put(data)

            time.sleep(min(1, ConfigurationManager.Shared.Config.RawData.DelayMs / 1000))

    def __del__(self):
        self.consumer_thread.join()
