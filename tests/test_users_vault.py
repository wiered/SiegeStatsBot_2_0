from __future__ import annotations

from typing import Set

from core.user import USERS_REDIS_INDEX_KEY, UsersVault, User


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.sets: dict[str, set[str]] = {}
        self.persisted: list[str] = []

    def get(self, key: str) -> str | None:
        return self.values.get(key)

    def set(self, key: str, value: str) -> None:
        self.values[key] = value

    def persist(self, key: str) -> None:
        self.persisted.append(key)

    def sadd(self, key: str, value: str) -> None:
        self.sets.setdefault(key, set()).add(value)

    def smembers(self, key: str) -> Set[str]:
        return self.sets.get(key, set())

    def delete(self, key: str) -> None:
        self.values.pop(key, None)

    def srem(self, key: str, value: str) -> None:
        self.sets.setdefault(key, set()).discard(value)


def set_fake_redis(vault: UsersVault, fake_redis: FakeRedis) -> None:
    setattr(vault, "_UsersVault__redis", fake_redis)


def test_users_vault_stores_authorized_user_without_ttl() -> None:
    vault = UsersVault()
    fake_redis = FakeRedis()
    set_fake_redis(vault, fake_redis)

    vault.add_user(User(d_id=123, siege_id="pollz"))

    assert fake_redis.values["users:v1:user:123"] == '{"siege_id":"pollz","d_id":123}'
    assert fake_redis.sets[USERS_REDIS_INDEX_KEY] == {"123"}
    assert fake_redis.persisted == ["users:v1:user:123", USERS_REDIS_INDEX_KEY]


def test_users_vault_loads_user_from_redis() -> None:
    first_vault = UsersVault()
    fake_redis = FakeRedis()
    set_fake_redis(first_vault, fake_redis)
    first_vault.add_user(User(d_id=123, siege_id="pollz"))

    second_vault = UsersVault()
    set_fake_redis(second_vault, fake_redis)
    second_vault.load_instance_from_csv()

    user = second_vault.get_user(123)
    assert user is not None
    assert user.d_id == 123
    assert user.siege_id == "pollz"


def test_users_vault_reads_user_from_redis_each_time() -> None:
    vault = UsersVault()
    fake_redis = FakeRedis()
    set_fake_redis(vault, fake_redis)

    vault.add_user(User(d_id=123, siege_id="pollz"))
    first_user = vault.get_user(123)
    fake_redis.values["users:v1:user:123"] = '{"siege_id":"updated","d_id":123}'
    second_user = vault.get_user(123)

    assert first_user is not None
    assert first_user.siege_id == "pollz"
    assert second_user is not None
    assert second_user.siege_id == "updated"
