class Config:
    def __init__(self):
        self.debug = {
            "debug": False,
            "to_files": False,
            "debug_messages": False
        }
        self.backend = {
            "port": 9838
        }
        self.http = {
            "enabled": True,
            "port": 8888,
            "show_account_names": False
        }
        self.raw_data = {
            "enabled": False,
            "webhook_url": "",
            "delay_ms": 5000
        }
        self.mysql = {
            "enabled": False,
            "connection_string": "server=localhost; port=3306; database=mysqldotnet; user=mysqldotnetuser; password=Pa55w0rd!; Persist Security Info=false; Connect Timeout=300"
        }
        self.mad_export = {
            "enabled": False,
            "connection_string": "server=localhost; port=3306; database=mysqldotnet; user=mysqldotnetuser; password=Pa55w0rd!; Persist Security Info=false; Connect Timeout=300"
        }
        self.encounter = {
            "enabled": False,
            "save_to_database": False,
            "discord_webhooks": [
                {
                    "webhook_url": "discord webhook url",
                    "filter_by_iv": False,
                    "only_equal": False,
                    "min_attack_iv": 0,
                    "min_defense_iv": 0,
                    "min_stamina_iv": 0,
                    "filter_by_location": False,
                    "latitude": 0.1,
                    "longitude": 0.1,
                    "distance_in_km": 20,
                    "custom_link": {
                        "title": "Custom Link",
                        "link": ""
                    }
                }
            ]
        }


