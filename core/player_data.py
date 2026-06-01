from __future__ import annotations

from typing import Any

from core.player_data_models import (
    NormalizedPlayerData,
    NormalizedProfile,
    NormalizedRankedSeasonRecord,
    NormalizedSeasonCollection,
)


class Profile:
    def __init__(self, profile: NormalizedProfile | None = None) -> None:
        profile = profile or NormalizedProfile()

        self.display_name = profile.display_name
        self.level = profile.level
        self.platform_slug = profile.platform_slug
        self.avatar_url = profile.avatar_url
        self.profile_url = profile.profile_url
        self.user_id = profile.display_name

    def __repr__(self) -> str:
        return (
            f"========{self.display_name}========\n"
            f"Platform: {self.platform_slug}\n"
            f"Level: {self.level}\n"
        )


class RankedSeasonRecord:
    def __init__(self, record: NormalizedRankedSeasonRecord | None = None) -> None:
        record = record or NormalizedRankedSeasonRecord()

        self.mode_slug = record.mode_slug
        self.season_id = record.season_id
        self.season_slug = record.season_slug
        self.season_name = record.season_name
        self.region_slug = record.region_slug
        self.rank_slug = record.rank_slug
        self.max_rank_slug = record.max_rank_slug
        self.rank_image_url = record.rank_image_url
        self.kills = record.kills
        self.deaths = record.deaths
        self.kd = record.kd
        self.wins = record.wins
        self.losses = record.losses
        self.wl = record.wl
        self.abandons = record.abandons
        self.mmr = record.mmr
        self.max_mmr = record.max_mmr
        self.mmr_change = record.mmr_change
        self.mmr_point = record.mmr_point
        self.champion_position = record.champion_position

    @property
    def season_key(self) -> str:
        return str(self.season_id or self.season_slug)

    def __repr__(self) -> str:
        return (
            f"Season: {self.season_slug}\n"
            f"Mode: {self.mode_slug}\n"
            f"Region: {self.region_slug}\n"
            f"Rank: {self.rank_slug}\n"
            f"Max Rank: {self.max_rank_slug}\n"
            f"Kills: {self.kills}\n"
            f"Deaths: {self.deaths}\n"
            f"KD: {self.kd}\n"
            f"Wins: {self.wins}\n"
            f"Losses: {self.losses}\n"
            f"WL: {self.wl}\n"
            f"Abandons: {self.abandons}\n"
            f"RP: {self.mmr}\n"
            f"Max RP: {self.max_mmr}\n"
            f"RP Change: {self.mmr_point}{self.mmr_change}\n"
            f"Champion Position: {self.champion_position}\n"
        )


class CurrentSeasonRecords:
    def __init__(
        self,
        records: NormalizedSeasonCollection | None = None,
    ) -> None:
        records = records or NormalizedSeasonCollection()
        self.ranked = RankedSeasonRecord(records.ranked)

    def __repr__(self) -> str:
        return f"Ranked:\n{self.ranked}"


class PastSeasonRankedRecords:
    def __init__(
        self,
        records: list[NormalizedRankedSeasonRecord] | None = None,
    ) -> None:
        self.seasons = [RankedSeasonRecord(record) for record in records or []]
        self.keys = [record.season_key for record in self.seasons]
        self.labels = {record.season_key: record.season_slug for record in self.seasons}

    def __getitem__(self, key: int) -> RankedSeasonRecord | None:
        try:
            return self.seasons[key]
        except IndexError:
            return None

    def get(self, key: str) -> RankedSeasonRecord:
        for record in self.seasons:
            if key in {record.season_key, record.season_slug, record.season_name}:
                return record
        return self.seasons[0] if self.seasons else RankedSeasonRecord()


class PlayerData:
    def __init__(self, data: NormalizedPlayerData | dict[str, Any] | None):
        self.normalized = self.__coerce_data(data)
        self.profile = Profile(self.normalized.profile)
        self.name = self.normalized.name or self.profile.display_name
        self.current_season_records = CurrentSeasonRecords(
            self.normalized.current_season_records
        )
        self.past_season_ranked_records = PastSeasonRankedRecords(
            self.normalized.past_season_ranked_records
        )
        self.r6data_url = self.normalized.r6data_url or self.profile.profile_url
        self.is_full = True

    @property
    def seasons(self) -> list[str]:
        return self.past_season_ranked_records.keys

    @property
    def season_labels(self) -> dict[str, str]:
        return self.past_season_ranked_records.labels

    @property
    def rank(self) -> str:
        return self.normalized.rank or self.current_season_records.ranked.rank_slug

    def get_current_season_record(self) -> str:
        return f"Player: {self.name}\n{self.current_season_records}"

    def get_season_record(self, season: str) -> RankedSeasonRecord:
        if not season or season == "Current Season":
            return self.current_season_records.ranked
        return self.past_season_ranked_records.get(season)

    def __repr__(self) -> str:
        return f"Player: {self.name}\n{self.profile}"

    def __coerce_data(
        self,
        data: NormalizedPlayerData | dict[str, Any] | None,
    ) -> NormalizedPlayerData:
        if isinstance(data, NormalizedPlayerData):
            return data
        if isinstance(data, dict) and data:
            return NormalizedPlayerData.model_validate(data)
        return NormalizedPlayerData()
