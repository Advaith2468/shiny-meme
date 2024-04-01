import json
import os

class ConfigurationManager:
    _shared_instance = None

    @staticmethod
    def shared():
        if ConfigurationManager._shared_instance is None:
            ConfigurationManager._shared_instance = ConfigurationManager()
        return ConfigurationManager._shared_instance

    def __init__(self):
        self.json_source = os.path.join(os.getcwd(), 'Config.json')
        self.config = self.load_config()
        if not os.path.exists(self.json_source):
            self.save()
        # Assuming Config.Encounter.DiscordWebhooks is a list and removing the first element
        if self.config.get("Encounter", {}).get("DiscordWebhooks", None):
            self.config["Encounter"]["DiscordWebhooks"].pop(0)
        print("Config was loaded!")

    def load_config(self):
        try:
            with open(self.json_source, 'r') as config_file:
                return json.load(config_file)
        except FileNotFoundError:
            return {}

    def save(self):
        with open(self.json_source, 'w') as config_file:
            json.dump(self.config, config_file, indent=4)
        print("Config was created!")


