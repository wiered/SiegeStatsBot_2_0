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
    map_player,
    rank_points_to_rank,
    seasonal_rp_change,
)
from core.player_data_models import (
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


def test_rank_points_to_rank_uses_highest_matching_threshold() -> None:
    assert rank_points_to_rank(0) == "unranked"
    assert rank_points_to_rank(999) == "unranked"
    assert rank_points_to_rank(2203) == "silver-3"
    assert rank_points_to_rank(4500) == "champion"


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
