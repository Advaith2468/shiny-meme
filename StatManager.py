from typing import Dict

class StatManager:
    _shared_instance = None

    @staticmethod
    def shared_instance():
        if StatManager._shared_instance is None:
            StatManager._shared_instance = StatManager()
        return StatManager._shared_instance

    def __init__(self):
        self.stat_dictionary: Dict[str, Stats] = {}

    def get_entry(self, acc):
        if acc not in self.stat_dictionary:
            self.stat_dictionary[acc] = Stats(acc)
        return self.stat_dictionary[acc]

    def remove_entry(self, acc):
        if acc in self.stat_dictionary:
            del self.stat_dictionary[acc]

    def get_all_entries(self):
        return self.stat_dictionary

    def contains_account(self, acc):
        return acc in self.stat_dictionary
