import datetime

class Stats:
    def __init__(self, acc=None):
        self.account_name = acc
        self.connection_timestamp = int(datetime.datetime.utcnow().timestamp())
        self.shiny_pokemon = 0
        self.caught_pokemon = 0
        self.xp_total = 0
        self.stardust_total = 0
        self.spinned_pokestops = 0
        self.fleet_pokemon = 0

    @property
    def now(self):
        return int(datetime.datetime.utcnow().timestamp())

    @property
    def days(self):
        return (self.now - self.connection_timestamp) / 3600 / 24

    @property
    def hours(self):
        return (self.now - self.connection_timestamp) / 3600

    @property
    def xp_per_hour(self):
        return int(self.xp_total / self.hours) if self.hours else 0

    @property
    def stardust_per_hour(self):
        return int(self.stardust_total / self.hours) if self.hours else 0

    @property
    def xp_per_day(self):
        return int(self.xp_total / self.days) if self.days else 0

    @property
    def stardust_per_day(self):
        return int(self.stardust_total / self.days) if self.days else 0

    @property
    def caught_pokemon_per_day(self):
        return int(self.caught_pokemon / self.days) if self.days else 0

    @property
    def spinned_pokestops_per_day(self):
        return int(self.spinned_pokestops / self.days) if self.days else 0

    def add_stardust(self, stardust):
        self.stardust_total += stardust

    def add_xp(self, xp):
        self.xp_total += xp

    def add_spinned_pokestop(self):
        self.spinned_pokestops += 1

    def to_dict(self):
        return {
            "account_name": self.account_name,
            "connection_timestamp": self.connection_timestamp,
            "shiny_pokemon": self.shiny_pokemon,
            "caught_pokemon": self.caught_pokemon,
            "xp_total": self.xp_total,
            "stardust_total": self.stardust_total,
            "spinned_pokestops": self.spinned_pokestops,
            "fleet_pokemon": self.fleet_pokemon,
            "xp_per_hour": self.xp_per_hour,
            "stardust_per_hour": self.stardust_per_hour,
            "xp_per_day": self.xp_per_day,
            "stardust_per_day": self.stardust_per_day,
            "caught_pokemon_per_day": self.caught_pokemon_per_day,
            "spinned_pokestops_per_day": self.spinned_pokestops_per_day
        }
