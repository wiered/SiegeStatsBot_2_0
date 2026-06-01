from pydantic import BaseModel, Field


class NormalizedProfile(BaseModel):
    display_name: str = "N/A"
    level: int = 0
    platform_slug: str = "uplay"
    avatar_url: str = ""
    profile_url: str = ""


class NormalizedRankedSeasonRecord(BaseModel):
    mode_slug: str = "ranked"
    season_id: int = 0
    season_slug: str = "N/A"
    season_name: str = "N/A"
    region_slug: str = "global"
    rank_slug: str = "unranked"
    max_rank_slug: str = "unranked"
    rank_image_url: str = ""
    kills: int = 0
    deaths: int = 0
    kd: float = 0.0
    wins: int = 0
    losses: int = 0
    wl: float = 0.0
    abandons: int = 0
    mmr: int = 0
    max_mmr: int = 0
    mmr_change: int = 0
    mmr_point: str = "ᐅ"
    champion_position: int = 1000


class NormalizedSeasonOption(BaseModel):
    season_id: int = 0
    season_slug: str = "N/A"
    season_name: str = "N/A"


class NormalizedSeasonCollection(BaseModel):
    ranked: NormalizedRankedSeasonRecord = Field(
        default_factory=NormalizedRankedSeasonRecord
    )


class NormalizedPlayerData(BaseModel):
    name: str = "N/A"
    profile: NormalizedProfile = Field(default_factory=NormalizedProfile)
    current_season_records: NormalizedSeasonCollection = Field(
        default_factory=NormalizedSeasonCollection
    )
    past_season_ranked_records: list[NormalizedRankedSeasonRecord] = Field(
        default_factory=list
    )
    seasons: list[NormalizedSeasonOption] = Field(default_factory=list)
    rank: str = "unranked"
    r6data_url: str = ""
