from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from POGOProtos.Rpc import HoloPokemonId_pb2, PokemonDisplayProto_pb2

class LogEntryType(Enum):
    Pokemon = 1
    Quest = 2
    Egg = 3
    Fort = 4
    FeedBerry = 5
    EvolvePokemon = 6
    Rocket = 7
    Raid = 8

@dataclass
class LogEntry:
    Id: int
    SessionId: int
    Session: Session  # You need to define the Session class
    LogEntryType: LogEntryType
    CaughtSuccess: bool
    PokemonUniqueId: int
    PokemonName: HoloPokemonId_pb2
    Attack: int
    Defense: int
    Stamina: int
    XpReward: int
    StardustReward: int
    CandyAwarded: int
    Shiny: bool
    Shadow: bool
    Costume: PokemonDisplayProto_pb2.Types.Costume
    Form: PokemonDisplayProto_pb2.Types.Form
    Timestamp: datetime
