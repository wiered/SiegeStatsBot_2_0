from pydantic import BaseModel, ConfigDict, Field, field_validator


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
