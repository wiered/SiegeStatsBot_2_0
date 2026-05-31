from typing import Any

from pydantic import BaseModel, ConfigDict, Field, RootModel


class ParserModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class RankedSeasonRecord(ParserModel):
    season: str
    rank: str
    max_rank: str
    rank_points: int
    max_rank_points: int


class RankedSeasonModeRecord(ParserModel):
    season: str
    mode: str
    matches: int
    wins: int
    losses: int
    abandons: int
    wr: float
    kills: int
    deaths: int
    assists: int
    headshots: int
    kd: float
    kda: float
    kpm: float
    hs: float


class PlayerProfile(ParserModel):
    id: str
    user_id: str
    username: str
    platform: str
    level: int
    hs: float
    ranked_season_record: RankedSeasonRecord | None = None
    ranked_season_mode_record: RankedSeasonModeRecord | None = None
    bans: list[Any] = Field(default_factory=list)
    external_bans: list[Any] = Field(default_factory=list)


class PlayerSearchResult(ParserModel):
    type: str
    profile: PlayerProfile


class PlayerSearchResponse(
    RootModel[list[PlayerSearchResult] | dict[str, PlayerSearchResult]]
):
    pass
