from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class R6DataModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class AccountInfoProfile(R6DataModel):
    xp: int = 0
    level: int = 0


class AccountInfoLinkedProfile(R6DataModel):
    platform_type: str = Field(default="", alias="platformType")
    name_on_platform: str = Field(default="", alias="nameOnPlatform")


class AccountInfoResponse(R6DataModel):
    xp: int = 0
    level: int = 0
    profile: AccountInfoProfile | None = None
    profiles: list[AccountInfoLinkedProfile] = Field(default_factory=list)
    profile_picture: str = Field(default="", alias="profilePicture")


class StatValue(R6DataModel):
    value: int | float = 0
    display_value: str = Field(default="", alias="displayValue")

    @field_validator("value", mode="before")
    @classmethod
    def default_missing_value(cls, value: int | float | None) -> int | float:
        return 0 if value is None else value

    @field_validator("display_value", mode="before")
    @classmethod
    def default_missing_display_value(cls, value: str | None) -> str:
        return "" if value is None else value


class SegmentStats(R6DataModel):
    kills: StatValue | None = None
    deaths: StatValue | None = None
    kd_ratio: StatValue | None = Field(default=None, alias="kdRatio")
    matches_won: StatValue | None = Field(default=None, alias="matchesWon")
    matches_lost: StatValue | None = Field(default=None, alias="matchesLost")
    matches_played: StatValue | None = Field(default=None, alias="matchesPlayed")
    rank_points: StatValue | None = Field(default=None, alias="rankPoints")
    max_rank_points: StatValue | None = Field(default=None, alias="maxRankPoints")


class SegmentAttributes(R6DataModel):
    season: int | None = None
    gamemode: str = ""
    session_type: str = Field(default="", alias="sessionType")
    region: str = ""


class SegmentMetadata(R6DataModel):
    name: str = ""
    color: str = ""
    rank_type: str = Field(default="", alias="rankType")
    short_name: str = Field(default="", alias="shortName")
    season_name: str = Field(default="", alias="seasonName")


class Segment(R6DataModel):
    type: str = ""
    stats: SegmentStats = Field(default_factory=SegmentStats)
    metadata: SegmentMetadata = Field(default_factory=SegmentMetadata)
    attributes: SegmentAttributes = Field(default_factory=SegmentAttributes)


class StatsMetadata(R6DataModel):
    current_season: int | None = Field(default=None, alias="currentSeason")
    clearance_level: int | None = Field(default=None, alias="clearanceLevel")
    battlepass_level: int | None = Field(default=None, alias="battlepassLevel")


class PlatformInfo(R6DataModel):
    platform_slug: str = Field(default="", alias="platformSlug")
    platform_user_id: str = Field(default="", alias="platformUserId")
    platform_user_handle: str = Field(default="", alias="platformUserHandle")
    avatar_url: str = Field(default="", alias="avatarUrl")


class StatsData(R6DataModel):
    metadata: StatsMetadata = Field(default_factory=StatsMetadata)
    segments: list[Segment] = Field(default_factory=list)
    platform_info: PlatformInfo | None = Field(default=None, alias="platformInfo")


class StatsResponse(R6DataModel):
    data: StatsData

    @model_validator(mode="before")
    @classmethod
    def normalize_stats_payload(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value

        if "data" in value:
            data = value.get("data")
            if not isinstance(data, dict):
                return value
            merged_data = {
                **data,
                **{
                    key: value[key]
                    for key in ("metadata", "segments", "platformInfo")
                    if key in value
                },
            }
            return {**value, "data": merged_data}

        if {"metadata", "segments", "platformInfo"} & value.keys():
            return {"data": value}

        normalized_data = _normalize_raw_platform_stats(value)
        if normalized_data is None:
            return value
        return {"data": normalized_data}


def _normalize_raw_platform_stats(value: dict[str, Any]) -> dict[str, Any] | None:
    platform_profiles = value.get("platform_families_full_profiles")
    if not isinstance(platform_profiles, list):
        return None

    segments: list[dict[str, Any]] = []
    current_season: int | None = None
    for platform_profile in platform_profiles:
        if not isinstance(platform_profile, dict):
            continue
        boards = platform_profile.get("board_ids_full_profiles")
        if not isinstance(boards, list):
            continue

        for board in boards:
            if not isinstance(board, dict):
                continue
            session_type = _normalize_raw_board_id(board.get("board_id"))
            full_profiles = board.get("full_profiles")
            if not isinstance(full_profiles, list):
                continue

            for full_profile in full_profiles:
                if not isinstance(full_profile, dict):
                    continue
                season_id = _to_int_or_none(full_profile.get("season_id"))
                if session_type == "ranked" and current_season is None:
                    current_season = season_id
                segments.append(
                    {
                        "type": "season",
                        "stats": _normalize_raw_stats(full_profile),
                        "metadata": {},
                        "attributes": {
                            "season": season_id,
                            "gamemode": f"pvp_{session_type}",
                            "sessionType": session_type,
                            "region": "global",
                        },
                    }
                )

    return {"metadata": {"currentSeason": current_season}, "segments": segments}


def _normalize_raw_stats(full_profile: dict[str, Any]) -> dict[str, dict[str, Any]]:
    profile = _dict_or_empty(full_profile.get("profile"))
    season_statistics = _dict_or_empty(full_profile.get("season_statistics"))
    match_outcomes = _dict_or_empty(season_statistics.get("match_outcomes"))

    kills = _first_value(season_statistics, profile, "kills")
    deaths = _first_value(season_statistics, profile, "deaths")
    wins = _first_value(match_outcomes, profile, "wins")
    losses = _first_value(match_outcomes, profile, "losses")
    abandons = _first_value(match_outcomes, profile, "abandons", "abandon")
    played = sum(_to_int_or_zero(value) for value in (wins, losses, abandons))

    return {
        "kills": _stat_value(kills),
        "deaths": _stat_value(deaths),
        "kdRatio": _stat_value(_kd_ratio(kills, deaths)),
        "matchesWon": _stat_value(wins),
        "matchesLost": _stat_value(losses),
        "matchesPlayed": _stat_value(played),
        "rankPoints": _stat_value(profile.get("rank_points")),
        "maxRankPoints": _stat_value(profile.get("max_rank_points")),
    }


def _normalize_raw_board_id(value: Any) -> str:
    board_id = value if isinstance(value, str) else ""
    return board_id or "ranked"


def _dict_or_empty(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _first_value(*sources: dict[str, Any] | str) -> Any:
    keys = [source for source in sources if isinstance(source, str)]
    for source in sources:
        if not isinstance(source, dict):
            continue
        for key in keys:
            if key in source:
                return source[key]
    return None


def _stat_value(value: Any) -> dict[str, Any]:
    return {"value": 0 if value is None else value}


def _kd_ratio(kills: Any, deaths: Any) -> float:
    death_count = _to_int_or_zero(deaths)
    if death_count == 0:
        return 0.0
    return _to_int_or_zero(kills) / death_count


def _to_int_or_none(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)


def _to_int_or_zero(value: Any) -> int:
    return _to_int_or_none(value) or 0


class SeasonalRankMetadata(R6DataModel):
    rank: str = ""
    color: str = ""
    image_url: str = Field(default="", alias="imageUrl")


class SeasonalHistoryValue(R6DataModel):
    value: int | float = 0
    metadata: SeasonalRankMetadata = Field(default_factory=SeasonalRankMetadata)
    display_name: str = Field(default="", alias="displayName")
    display_type: str = Field(default="", alias="displayType")
    display_value: str = Field(default="", alias="displayValue")


class SeasonalHistoryMetadata(R6DataModel):
    key: str = ""
    name: str = ""
    description: str | None = None


class SeasonalHistory(R6DataModel):
    data: list[tuple[str, SeasonalHistoryValue]] = Field(default_factory=list)
    metadata: SeasonalHistoryMetadata = Field(default_factory=SeasonalHistoryMetadata)


class SeasonalStatsData(R6DataModel):
    history: SeasonalHistory = Field(default_factory=SeasonalHistory)
    expiry_date: str = Field(default="", alias="expiryDate")
    best_matches: list[dict] | None = Field(default=None, alias="bestMatches")
    leaderboard: dict | None = None


class SeasonalStatsResponse(R6DataModel):
    data: SeasonalStatsData
