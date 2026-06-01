import logging
import json
from pathlib import Path

import redis
from redis.exceptions import RedisError

from config import Config
from core import csv_addon, parser, type_helpers
from core.player_data import PlayerData
from core.player_data_models import NormalizedPlayerData

USERS_CSV_PATH = Path(__file__).resolve().parents[1] / "db" / "users.csv"
USERS_REDIS_INDEX_KEY = "users:v1:index"
USERS_REDIS_KEY_PREFIX = "users:v1:user:"


class UsersVault:
    def __init__(self):
        self.__redis: redis.Redis | None = None

    @property
    def redis(self) -> redis.Redis | None:
        if self.__redis is not None:
            return self.__redis

        try:
            config = Config()
            if not config.redis_enabled:
                return None

            client = redis.from_url(config.redis_url, decode_responses=True)
            client.ping()
        except (OSError, RedisError, ValueError):
            logging.exception("Redis users storage is unavailable")
            return None

        self.__redis = client
        return self.__redis

    @property
    def users(self) -> dict:
        return self.__load_users_from_redis__()

    @property
    def keys(self):
        return self.__load_user_ids_from_redis__()

    def add_user(self, user):
        """Add user to UsersVault

        Args:
            user (User): User object
        """

        self.__save_user_to_redis__(user)

    def load_instance_from_csv(self):
        """Instantiate UsersVault from Redis, then migrate legacy csv if needed.

        Raises:
            FileNotFoundError: if csv file not found
        """

        logging.info("Instantiating users from Redis")
        if not self.users:
            self.__load_users__()
        logging.info("Users loaded")

    def save_instance_to_csv(self):
        """Persist all authorized users to Redis."""

        for user in self.iter_users():
            self.__save_user_to_redis__(user)
        logging.info("All userdata saved")

    def get_user(self, d_id: int):
        """Get user by discord id

        Args:
            d_id (int): user's discord ID

        Returns:
            User: User object
        """

        d_id = int(d_id)
        return self.__load_user_from_redis__(d_id)

    def delete_by_dID(self, d_id: int) -> None:
        """Delete user by his discord ID

        Args:
            d_id (int): user's discord ID
        """

        d_id = int(d_id)
        client = self.redis
        if client is None:
            return

        try:
            client.delete(self.__get_redis_user_key__(d_id))
            client.srem(USERS_REDIS_INDEX_KEY, str(d_id))
        except RedisError:
            logging.exception("Failed to delete user %s from Redis", d_id)

    def is_authorized(self, d_id: int) -> bool:
        """Check if user is authorized

        Args:
            d_id (int): user's discord ID

        Returns:
            bool: True if user is authorized, False otherwise
        """

        return self.get_user(d_id) is not None

    def iter_users(self):
        """Yield authorized users from Redis without retaining them in memory."""

        yield from self.__load_users_from_redis__().values()

    def __load_users_from_redis__(self) -> dict[int, "User"]:
        """Load all authorized users from Redis."""

        client = self.redis
        if client is None:
            return {}

        d_ids = self.__load_user_ids_from_redis__()

        users: dict[int, User] = {}
        for d_id in d_ids:
            user = self.__load_user_from_redis__(d_id)
            if user is not None:
                users[user.d_id] = user

        logging.info("Users loaded from Redis")
        return users

    def __load_user_ids_from_redis__(self) -> set[int]:
        client = self.redis
        if client is None:
            return set()

        try:
            return {int(d_id) for d_id in client.smembers(USERS_REDIS_INDEX_KEY)}
        except (RedisError, ValueError):
            logging.exception("Failed to load users index from Redis")
            return set()

    def __load_user_from_redis__(self, d_id: int):
        client = self.redis
        if client is None:
            return None

        try:
            raw_user = client.get(self.__get_redis_user_key__(d_id))
        except RedisError:
            logging.exception("Failed to load user %s from Redis", d_id)
            return None

        if raw_user is None:
            return None

        try:
            user_data = json.loads(raw_user)
        except json.JSONDecodeError:
            logging.exception("Invalid Redis user payload for %s", d_id)
            return None

        return User(
            siege_id=str(user_data.get("siege_id", "")),
            d_id=type_helpers.get_d_id(user_data),
        )

    def __save_user_to_redis__(self, user) -> None:
        client = self.redis
        if client is None:
            return

        key = self.__get_redis_user_key__(user.d_id)
        raw_user = json.dumps(
            self.__generate_user_data__(user),
            separators=(",", ":"),
            ensure_ascii=False,
        )
        try:
            client.set(key, raw_user)
            client.persist(key)
            client.sadd(USERS_REDIS_INDEX_KEY, str(user.d_id))
            client.persist(USERS_REDIS_INDEX_KEY)
        except RedisError:
            logging.exception("Failed to save user %s to Redis", user.d_id)

    def __get_redis_user_key__(self, d_id: int) -> str:
        return f"{USERS_REDIS_KEY_PREFIX}{int(d_id)}"

    def __load_users__(self):
        """Load all authorized users from csv"""

        if not USERS_CSV_PATH.exists():
            logging.warning("Users csv not found: %s", USERS_CSV_PATH)
            return

        items = csv_addon.load_from_csv(USERS_CSV_PATH)
        if len(items) == 0:
            logging.warning("No users in csv")
            return
        for item in items:
            self.add_user(
                User(
                    siege_id=str(item.get("siege_id")),
                    d_id=type_helpers.get_d_id(item),
                )
            )
        logging.info("Users loaded from csv")

    def __generate_user_data__(self, user) -> dict:
        """Generate user data from json

        Args:
            user (core.user.User): user object

        Returns:
            dict: std user data
        """

        return {
            "siege_id": user.siege_id,
            "d_id": user.d_id,
        }


class User:
    def __init__(
        self,
        d_id: int = 0,
        siege_id: str = "",
        player_data: NormalizedPlayerData | None = None,
    ):
        self.__d_id = d_id
        self.__siege_id = siege_id
        self.__full_json: dict = {}
        self.__normalized_data = NormalizedPlayerData()
        self.player_data = PlayerData(self.__normalized_data)

        if player_data is not None:
            self.set_player_data(player_data)

    @classmethod
    async def create(cls, d_id: int = 0, siege_id: str = ""):
        user = cls(d_id=d_id, siege_id=siege_id)
        await user.parse_data()
        return user

    @property
    def name(self) -> str:
        return self.data.name

    @property
    def d_id(self) -> int:
        return self.__d_id

    @property
    def siege_id(self) -> str:
        return self.__siege_id

    @property
    def rank(self) -> str:
        return self.data.rank

    @property
    def full_json(self) -> dict:
        if self.__full_json:
            return self.__full_json
        return {}

    @property
    def data(self) -> PlayerData:
        return self.player_data

    async def parse_data(self):
        """Parse player data from R6Data."""

        async with parser.Parser() as _parser:
            parsed_player = await _parser.parse_player(self.__siege_id)

        if isinstance(parsed_player, NormalizedPlayerData):
            self.set_player_data(parsed_player)
        elif isinstance(parsed_player, dict):
            self.__full_json = parsed_player
            self.player_data = PlayerData(parsed_player)

        logging.info(f"Stats parsed: {self.rank}")

    def set_player_data(self, parsed_player: NormalizedPlayerData) -> None:
        self.__normalized_data = parsed_player
        self.__full_json = parsed_player.model_dump()
        self.player_data = PlayerData(parsed_player)
        if parsed_player.name and parsed_player.name != "N/A":
            self.__siege_id = parsed_player.name

    def __repr__(self) -> str:
        return f"User({self.__d_id}, {self.__siege_id})"
