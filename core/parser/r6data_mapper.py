from urllib.parse import quote

from core.parser.models import (
    AccountInfoResponse,
    SeasonalHistoryValue,
    SeasonalStatsResponse,
    Segment,
    StatValue,
    StatsResponse,
)
from core.player_data_models import (
    NormalizedPlayerData,
    NormalizedProfile,
    NormalizedRankedSeasonRecord,
    NormalizedSeasonCollection,
    NormalizedSeasonOption,
)


R6DATA_STATS_URL = (
    "https://r6data.com/stats?username={username}&platform={platform}&tab=1"
)
R6DATA_RANK_IMAGE_URL = "https://r6data.com/assets/img/r6_ranks_img/{rank}.webp"

RANK_THRESHOLDS = (
    (0, "unranked"),
    (1000, "copper-5"),
    (1100, "copper-4"),
    (1200, "copper-3"),
    (1300, "copper-2"),
    (1400, "copper-1"),
    (1500, "bronze-5"),
    (1600, "bronze-4"),
    (1700, "bronze-3"),
    (1800, "bronze-2"),
    (1900, "bronze-1"),
    (2000, "silver-5"),
    (2100, "silver-4"),
    (2200, "silver-3"),
    (2300, "silver-2"),
    (2400, "silver-1"),
    (2500, "gold-5"),
    (2600, "gold-4"),
    (2700, "gold-3"),
    (2800, "gold-2"),
    (2900, "gold-1"),
    (3000, "platinum-5"),
    (3100, "platinum-4"),
    (3200, "platinum-3"),
    (3300, "platinum-2"),
    (3400, "platinum-1"),
    (3500, "emerald-5"),
    (3600, "emerald-4"),
    (3700, "emerald-3"),
    (3800, "emerald-2"),
    (3900, "emerald-1"),
    (4000, "diamond-5"),
    (4100, "diamond-4"),
    (4200, "diamond-3"),
    (4300, "diamond-2"),
    (4400, "diamond-1"),
    (4500, "champion"),
)


def rank_points_to_rank(value: int | float | None) -> str:
    rank = "unranked"
    points = _to_int(value)
    for threshold, rank_slug in RANK_THRESHOLDS:
        if points >= threshold:
            rank = rank_slug
        else:
            break
    return rank


def normalize_rank_name(rank_name: str) -> str:
    rank_name = rank_name.strip().lower()
    if not rank_name:
        return "unranked"
    return rank_name.replace(" ", "-")


def make_r6data_url(username: str, platform: str = "uplay") -> str:
    return R6DATA_STATS_URL.format(
        username=quote(username, safe=""),
        platform=quote(platform, safe=""),
    )


def map_account_info_to_profile(
    account_info: AccountInfoResponse,
    username: str,
    platform: str = "uplay",
) -> NormalizedProfile:
    linked_profile = account_info.profiles[0] if account_info.profiles else None
    display_name = (
        linked_profile.name_on_platform if linked_profile else username
    ) or username
    platform_slug = (
        linked_profile.platform_type if linked_profile else platform
    ) or platform
    level = account_info.level or (
        account_info.profile.level if account_info.profile else 0
    )

    return NormalizedProfile(
        display_name=display_name or "N/A",
        level=level,
        platform_slug=platform_slug,
        avatar_url=account_info.profile_picture,
        profile_url=make_r6data_url(display_name or username, platform),
    )


def map_player(
    account_info: AccountInfoResponse,
    stats: StatsResponse,
    seasonal_stats: SeasonalStatsResponse,
    seasons: StatsResponse,
    username: str,
    platform: str = "uplay",
) -> NormalizedPlayerData:
    profile = map_account_info_to_profile(account_info, username, platform)
    platform_info = stats.data.platform_info
    if platform_info is not None:
        display_name = platform_info.platform_user_handle or profile.display_name
        platform_slug = (
            _normalize_platform_slug(platform_info.platform_slug) or platform
        )
        profile = profile.model_copy(
            update={
                "display_name": display_name,
                "platform_slug": platform_slug,
                "avatar_url": platform_info.avatar_url or profile.avatar_url,
                "profile_url": make_r6data_url(display_name, platform),
            }
        )

    current_season = stats.data.metadata.current_season
    ranked_segments = [
        segment for segment in seasons.data.segments if _is_ranked_season_segment(segment)
    ]
    current_segment = _find_current_ranked_segment(
        ranked_segments,
        current_season,
    )

    current_record = map_ranked_segment_to_record(
        current_segment,
        seasonal_stats=seasonal_stats,
        current=True,
    )
    past_records = [
        map_ranked_segment_to_record(segment)
        for segment in sorted(
            ranked_segments,
            key=lambda item: item.attributes.season or 0,
            reverse=True,
        )
        if segment is not current_segment
    ]
    season_options = [
        NormalizedSeasonOption(
            season_id=record.season_id,
            season_slug=record.season_slug,
            season_name=record.season_name,
        )
        for record in past_records
    ]

    return NormalizedPlayerData(
        name=profile.display_name,
        profile=profile,
        current_season_records=NormalizedSeasonCollection(ranked=current_record),
        past_season_ranked_records=past_records,
        seasons=season_options,
        rank=current_record.rank_slug,
        r6data_url=profile.profile_url,
    )


def map_ranked_segment_to_record(
    segment: Segment | None,
    seasonal_stats: SeasonalStatsResponse | None = None,
    current: bool = False,
) -> NormalizedRankedSeasonRecord:
    if segment is None:
        return NormalizedRankedSeasonRecord()

    stats = segment.stats
    wins = _stat_int(stats.matches_won)
    losses = _stat_int(stats.matches_lost)
    played = _stat_int(stats.matches_played)
    mmr = _stat_int(stats.rank_points)
    max_mmr = _stat_int(stats.max_rank_points)
    rank_slug = rank_points_to_rank(mmr)
    rank_image_url = rank_image_for_slug(rank_slug)
    mmr_change = 0
    mmr_point = "ᐅ"

    if current and seasonal_stats is not None:
        latest_rank = latest_seasonal_rank(seasonal_stats)
        if latest_rank is not None:
            rank_slug = normalize_rank_name(latest_rank.metadata.rank)
            rank_image_url = latest_rank.metadata.image_url or rank_image_url

        raw_change = seasonal_rp_change(seasonal_stats)
        mmr_point = "ᐃ" if raw_change > 0 else "ᐁ" if raw_change < 0 else "ᐅ"
        mmr_change = abs(raw_change)

    return NormalizedRankedSeasonRecord(
        mode_slug=segment.attributes.session_type
        or _normalize_gamemode(segment.attributes.gamemode),
        season_id=segment.attributes.season or 0,
        season_slug=segment.metadata.name or "N/A",
        season_name=segment.metadata.season_name or segment.metadata.name or "N/A",
        region_slug=segment.attributes.region or "global",
        rank_slug=rank_slug,
        max_rank_slug=rank_points_to_rank(max_mmr),
        rank_image_url=rank_image_url,
        kills=_stat_int(stats.kills),
        deaths=_stat_int(stats.deaths),
        kd=_stat_float(stats.kd_ratio),
        wins=wins,
        losses=losses,
        wl=_win_loss_ratio(wins, losses),
        abandons=max(played - wins - losses, 0),
        mmr=mmr,
        max_mmr=max_mmr,
        mmr_change=mmr_change,
        mmr_point=mmr_point,
        champion_position=1000,
    )


def seasonal_rp_change(seasonal_stats: SeasonalStatsResponse) -> int:
    history = seasonal_stats.data.history.data
    if len(history) < 2:
        return 0
    return _to_int(history[0][1].value) - _to_int(history[1][1].value)


def latest_seasonal_rank(
    seasonal_stats: SeasonalStatsResponse,
) -> SeasonalHistoryValue | None:
    history = seasonal_stats.data.history.data
    if not history:
        return None
    return history[0][1]


def rank_image_for_slug(rank_slug: str) -> str:
    return R6DATA_RANK_IMAGE_URL.format(rank=rank_slug or "unranked")


def _is_ranked_season_segment(segment: Segment) -> bool:
    return segment.type == "season" and segment.attributes.session_type == "ranked"


def _find_current_ranked_segment(
    segments: list[Segment],
    current_season: int | None,
) -> Segment | None:
    for segment in segments:
        if segment.attributes.season == current_season:
            return segment
    return segments[0] if segments else None


def _stat_int(stat: StatValue | None) -> int:
    return _to_int(stat.value if stat is not None else 0)


def _stat_float(stat: StatValue | None) -> float:
    return _to_float(stat.value if stat is not None else 0)


def _to_int(value: int | float | None) -> int:
    if value is None:
        return 0
    return int(value)


def _to_float(value: int | float | None) -> float:
    if value is None:
        return 0.0
    return float(value)


def _win_loss_ratio(wins: int, losses: int) -> float:
    total = wins + losses
    if total == 0:
        return 0.0
    return wins / total


def _normalize_gamemode(gamemode: str) -> str:
    return gamemode.removeprefix("pvp_") or "ranked"


def _normalize_platform_slug(platform_slug: str) -> str:
    return "uplay" if platform_slug == "ubi" else platform_slug
