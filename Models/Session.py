from datetime import datetime
from typing import List
from dataclasses import dataclass
from POGOProtos.Rpc import Account

@dataclass
class Session:
    Id: int
    AccountId: int
    Account: Account
    StartTime: datetime
    EndTime: datetime
    TotalGainedXp: int = 0
    TotalGainedStardust: int = 0
    TotalMinutes: int = 0
    CaughtPokemon: int = 0
    EscapedPokemon: int = 0
    ShinyPokemon: int = 0
    Pokestops: int = 0
    Rockets: int = 0
    Raids: int = 0
    MaxIV: int = 0
    Shadow: int = 0
    LastUpdate: datetime
    LogEntrys: List[LogEntry] = []
