import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from core.parser.models import (
    AccountInfoResponse,
    SeasonalStatsResponse,
    StatsResponse,
)
from core.parser import Parser
from core.parser.r6data_mapper import (
    map_account_info_to_profile,
    map_player,
    map_ranked_segment_to_record,
    rank_points_to_rank,
    seasonal_rp_change,
)
from core.player_data import PlayerData
from core.player_data_models import (
    NormalizedProfile,
    NormalizedPlayerData,
    NormalizedRankedSeasonRecord,
    NormalizedSeasonCollection,
    NormalizedSeasonOption,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_FIXTURE_DIR = PROJECT_ROOT / "json_examples" / "jsons"
LOCAL_FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"


def load_fixture(name: str) -> dict:
    fixture_path = PROJECT_FIXTURE_DIR / name
    if not fixture_path.exists():
        fixture_path = LOCAL_FIXTURE_DIR / name

    with fixture_path.open(encoding="utf-8-sig") as fixture:
        return json.load(fixture)


def test_account_info_fixture_validates() -> None:
    response = AccountInfoResponse.model_validate(load_fixture("accountInfo.json"))

    assert response.level == 325
    assert response.profiles[0].name_on_platform == "wiered"
    assert response.profiles[0].platform_type == "uplay"
    assert response.profile_picture


def test_account_confirmation_payload_maps_to_normalized_profile() -> None:
    profile = map_account_info_to_profile(
        AccountInfoResponse.model_validate(load_fixture("accountInfo.json")),
        username="requested-name",
    )

    assert profile.display_name == "wiered"
    assert profile.platform_slug == "uplay"
    assert profile.level == 325
    assert profile.avatar_url
    assert profile.profile_url == (
        "https://r6data.com/stats?username=wiered&platform=uplay&tab=1"
    )


def test_stats_fixture_validates() -> None:
    response = StatsResponse.model_validate(load_fixture("pollz_data.json"))

    assert response.data.metadata.current_season == 41
    assert response.data.segments
    assert response.data.platform_info is not None
    assert response.data.platform_info.platform_user_handle == "pollz"


def test_stats_response_requires_data_container() -> None:
    with pytest.raises(ValidationError):
        StatsResponse.model_validate({})


def test_seasonal_stats_fixtures_validate() -> None:
    seasonal_response = SeasonalStatsResponse.model_validate(
        load_fixture("seasonal_data.json")
    )
    pollz_response = SeasonalStatsResponse.model_validate(
        load_fixture("pollz_seasonal.json")
    )

    assert seasonal_response.data.history.data[0][1].metadata.rank == "Silver 3"
    assert seasonal_response.data.history.metadata.key == "RankPoints"
    assert pollz_response.data.history.data[0][1].metadata.image_url


def test_seasonal_stats_response_requires_data_container() -> None:
    with pytest.raises(ValidationError):
        SeasonalStatsResponse.model_validate({})


def test_normalized_player_contract_contains_ui_and_role_fields() -> None:
    ranked = NormalizedRankedSeasonRecord(
        season_id=41,
        season_slug="Y11S1",
        season_name="Silent Hunt",
        rank_slug="silver-3",
        max_rank_slug="silver-3",
        mmr=2203,
    )
    season = NormalizedSeasonOption(
        season_id=ranked.season_id,
        season_slug=ranked.season_slug,
        season_name=ranked.season_name,
    )
    player = NormalizedPlayerData(
        name="wiered",
        current_season_records=NormalizedSeasonCollection(ranked=ranked),
        past_season_ranked_records=[ranked],
        seasons=[season],
        rank=ranked.rank_slug,
        r6data_url="https://r6data.com/stats?username=wiered&platform=uplay&tab=1",
    )

    assert player.current_season_records.ranked.mmr == 2203
    assert player.past_season_ranked_records[0].season_id == 41
    assert player.seasons[0].season_id == 41
    assert player.seasons[0].season_slug == "Y11S1"
    assert player.rank == "silver-3"
    assert player.r6data_url.startswith("https://r6data.com/")


def test_player_data_adapts_normalized_model_to_ui_contract() -> None:
    current = NormalizedRankedSeasonRecord(
        season_id=41,
        season_slug="Y11S1",
        season_name="Silent Hunt",
        rank_slug="silver-3",
        max_rank_slug="silver-2",
        rank_image_url="https://r6data.com/rank.webp",
        mmr=2203,
        max_mmr=2301,
        mmr_change=11,
        mmr_point="ᐁ",
    )
    past = NormalizedRankedSeasonRecord(
        season_id=40,
        season_slug="Y10S4",
        season_name="High Stakes",
        rank_slug="gold-5",
    )
    normalized = NormalizedPlayerData(
        name="wiered",
        profile=NormalizedProfile(
            display_name="wiered",
            level=325,
            platform_slug="uplay",
            avatar_url="https://example.test/avatar.webp",
            profile_url="https://r6data.com/stats?username=wiered&platform=uplay&tab=1",
        ),
        current_season_records=NormalizedSeasonCollection(ranked=current),
        past_season_ranked_records=[past],
        seasons=[
            NormalizedSeasonOption(
                season_id=40,
                season_slug="Y10S4",
                season_name="High Stakes",
            )
        ],
        rank=current.rank_slug,
        r6data_url="https://r6data.com/stats?username=wiered&platform=uplay&tab=1",
    )

    player = PlayerData(normalized)

    assert player.name == "wiered"
    assert player.profile.display_name == "wiered"
    assert player.profile.user_id == "wiered"
    assert player.current_season_records.ranked.mmr == 2203
    assert player.current_season_records.ranked.rank_slug == "silver-3"
    assert player.past_season_ranked_records.get("40").rank_slug == "gold-5"
    assert player.seasons == ["40"]
    assert player.season_labels == {"40": "Y10S4"}
    assert player.rank == "silver-3"


def test_rank_points_to_rank_uses_highest_matching_threshold() -> None:
    assert rank_points_to_rank(0) == "unranked"
    assert rank_points_to_rank(999) == "unranked"
    assert rank_points_to_rank(2203) == "silver-3"
    assert rank_points_to_rank(4500) == "champion"


def test_rank_points_to_rank_handles_threshold_boundaries() -> None:
    assert rank_points_to_rank(None) == "unranked"
    assert rank_points_to_rank(1000) == "copper-5"
    assert rank_points_to_rank(1099) == "copper-5"
    assert rank_points_to_rank(1100) == "copper-4"
    assert rank_points_to_rank(4499) == "diamond-1"
    assert rank_points_to_rank(4501) == "champion"


def test_seasonal_rp_change_uses_latest_two_history_points() -> None:
    response = SeasonalStatsResponse.model_validate(
        {
            "data": {
                "history": {
                    "data": [
                        ["2026-06-01T00:00:00+00:00", {"value": 2203}],
                        ["2026-05-31T00:00:00+00:00", {"value": 2214}],
                    ]
                }
            }
        }
    )

    assert seasonal_rp_change(response) == -11


def test_seasonal_data_fixture_defaults_to_zero_rp_change() -> None:
    response = SeasonalStatsResponse.model_validate(load_fixture("seasonal_data.json"))

    assert seasonal_rp_change(response) == 0


def test_current_and_past_ranked_seasons_are_mapped_from_segments() -> None:
    stats = StatsResponse.model_validate(
        {
            "data": {
                "metadata": {"currentSeason": 41},
                "segments": [
                    {
                        "type": "season",
                        "stats": {
                            "kills": {"value": 12},
                            "deaths": {"value": 6},
                            "kdRatio": {"value": 2.0},
                            "matchesWon": {"value": 4},
                            "matchesLost": {"value": 2},
                            "matchesPlayed": {"value": 7},
                            "rankPoints": {"value": 2200},
                            "maxRankPoints": {"value": 2300},
                        },
                        "metadata": {
                            "shortName": "Y11S1",
                            "seasonName": "Silent Hunt",
                        },
                        "attributes": {
                            "season": 41,
                            "gamemode": "pvp_ranked",
                            "sessionType": "ranked",
                        },
                    },
                    {
                        "type": "season",
                        "stats": {
                            "rankPoints": {"value": 2500},
                            "maxRankPoints": {"value": 2600},
                        },
                        "metadata": {
                            "shortName": "Y10S4",
                            "seasonName": "High Stakes",
                        },
                        "attributes": {
                            "season": 40,
                            "gamemode": "pvp_ranked",
                            "sessionType": "ranked",
                        },
                    },
                    {
                        "type": "season",
                        "stats": {
                            "rankPoints": {"value": 3000},
                            "maxRankPoints": {"value": 3100},
                        },
                        "metadata": {
                            "shortName": "Y10S3",
                            "seasonName": "Daybreak",
                        },
                        "attributes": {
                            "season": 39,
                            "gamemode": "pvp_ranked",
                            "sessionType": "ranked",
                        },
                    },
                    {
                        "type": "season",
                        "stats": {"rankPoints": {"value": 4500}},
                        "attributes": {
                            "season": 38,
                            "gamemode": "pvp_standard",
                            "sessionType": "standard",
                        },
                    },
                ],
            }
        }
    )
    player = map_player(
        account_info=AccountInfoResponse.model_validate(
            load_fixture("accountInfo.json")
        ),
        stats=stats,
        seasonal_stats=SeasonalStatsResponse.model_validate(
            {
                "data": {
                    "history": {
                        "data": [
                            [
                                "2026-06-01T00:00:00+00:00",
                                {
                                    "value": 2200,
                                    "metadata": {"rank": "Silver 3"},
                                },
                            ],
                            ["2026-05-31T00:00:00+00:00", {"value": 2191}],
                        ]
                    }
                }
            }
        ),
        username="wiered",
    )

    current = player.current_season_records.ranked
    assert current.season_id == 41
    assert current.rank_slug == "silver-3"
    assert current.mmr == 2200
    assert current.max_rank_slug == "silver-2"
    assert current.abandons == 1
    assert current.mmr_change == 9
    assert current.mmr_point == "ᐃ"
    assert [record.season_id for record in player.past_season_ranked_records] == [
        40,
        39,
    ]
    assert [season.season_id for season in player.seasons] == [40, 39]
    assert player.past_season_ranked_records[0].rank_slug == "gold-5"
    assert player.past_season_ranked_records[1].rank_slug == "platinum-5"


def test_missing_data_maps_to_defaults() -> None:
    response = StatsResponse.model_validate(
        {
            "data": {
                "metadata": {"currentSeason": 41},
                "segments": [
                    {
                        "type": "season",
                        "attributes": {
                            "season": 41,
                            "gamemode": "pvp_ranked",
                            "sessionType": "ranked",
                        },
                    }
                ],
            }
        }
    )
    record = map_ranked_segment_to_record(response.data.segments[0])

    assert record.mode_slug == "ranked"
    assert record.season_id == 41
    assert record.season_slug == "N/A"
    assert record.rank_slug == "unranked"
    assert record.max_rank_slug == "unranked"
    assert record.kills == 0
    assert record.deaths == 0
    assert record.kd == 0.0
    assert record.wins == 0
    assert record.losses == 0
    assert record.wl == 0.0
    assert record.abandons == 0
    assert record.mmr_change == 0
    assert record.mmr_point == "ᐅ"


def test_player_data_contract_does_not_expose_removed_old_provider_fields() -> None:
    player = PlayerData(NormalizedPlayerData())

    removed_fields = {
        "aliases",
        "display_ban",
        "general_records",
        "is_verified",
        "profile_views",
        "summary_graph_data",
    }

    assert all(not hasattr(player, field_name) for field_name in removed_fields)


def test_map_player_builds_complete_normalized_player_from_fixtures() -> None:
    player = map_player(
        account_info=AccountInfoResponse.model_validate(
            load_fixture("accountInfo.json")
        ),
        stats=StatsResponse.model_validate(load_fixture("pollz_data.json")),
        seasonal_stats=SeasonalStatsResponse.model_validate(
            load_fixture("pollz_seasonal.json")
        ),
        username="pollz",
    )

    ranked = player.current_season_records.ranked
    assert player.name == "pollz"
    assert player.profile.level == 325
    assert player.profile.platform_slug == "uplay"
    assert player.rank == "diamond-1"
    assert ranked.season_id == 41
    assert ranked.season_slug == "Y11S1"
    assert ranked.kills == 1014
    assert ranked.deaths == 719
    assert ranked.kd == 1.4102920723226704
    assert ranked.wins == 82
    assert ranked.losses == 83
    assert ranked.abandons == 6
    assert ranked.mmr == 4435
    assert ranked.max_rank_slug == "champion"
    assert ranked.mmr_change == 0
    assert ranked.rank_image_url.endswith("diamond-1.webp")


def test_parser_parse_player_returns_normalized_player(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    parser = Parser(api_key="")

    monkeypatch.setattr(
        parser,
        "get_account_info",
        lambda username: load_fixture("accountInfo.json"),
    )
    monkeypatch.setattr(
        parser,
        "get_stats",
        lambda username: load_fixture("pollz_data.json"),
    )
    monkeypatch.setattr(
        parser,
        "get_seasonal_stats",
        lambda username: load_fixture("pollz_seasonal.json"),
    )

    player = parser.parse_player("pollz")

    assert isinstance(player, NormalizedPlayerData)
    assert player.current_season_records.ranked.season_id == 41
    assert player.rank == "diamond-1"


def test_parser_get_account_profile_returns_confirmation_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    parser = Parser(api_key="")

    monkeypatch.setattr(
        parser,
        "get_account_info",
        lambda username, platform="uplay": load_fixture("accountInfo.json"),
    )

    profile = parser.get_account_profile("wiered")

    assert profile is not None
    assert profile.display_name == "wiered"
    assert profile.platform_slug == "uplay"
    assert profile.level == 325
    assert profile.profile_url == (
        "https://r6data.com/stats?username=wiered&platform=uplay&tab=1"
    )


def test_parser_get_account_profile_returns_none_without_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    parser = Parser(api_key="")

    monkeypatch.setattr(
        parser,
        "get_account_info",
        lambda username, platform="uplay": {},
    )

    assert parser.get_account_profile("missing") is None
