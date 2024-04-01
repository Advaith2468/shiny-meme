from datetime import datetime
from enum import Enum
from POGOProtos.Rpc import Team_pb2  # Import the Team enum from POGOProtos.Rpc

class Team(Enum):
    # Assuming Team_pb2.Team is the enum from POGOProtos.Rpc.Team
    # You may need to adjust the enum member names and values accordingly
    VALUE = Team_pb2.Team.VALUE
    # Define other enum members similarly if needed

class Account:
    def __init__(self):
        self.Id = None
        self.Name = ""
        self.HashedName = ""
        self.Level = 1
        self.Team = Team.VALUE  # Set appropriate default value for Team
        self.Pokecoins = 0
        self.Experience = 0
        self.NextLevelExp = 0
        self.Stardust = 0
        self.TotalGainedXp = 0
        self.TotalGainedStardust = 0
        self.TotalMinutes = 0
        self.CaughtPokemon = 0
        self.EscapedPokemon = 0
        self.ShinyPokemon = 0
        self.Pokestops = 0
        self.Rockets = 0
        self.Raids = 0
        self.MaxIV = 0
        self.Shadow = 0
        self.LastUpdate = datetime.now()
        self.Sessions = []

# Example of creating an Account instance
# account = Account()
