from dataclasses import dataclass
from datetime import datetime
from POGOProtos.Rpc import HoloPokemonId, PokemonDisplayProto

@dataclass
class Encounter:
    Id: int
    EncounterId: int
    PokemonName: HoloPokemonId
    Form: PokemonDisplayProto.Types.Form
    Attack: int
    Defense: int
    Stamina: int
    Longitude: float
    Latitude: float
    Timestamp: datetime
