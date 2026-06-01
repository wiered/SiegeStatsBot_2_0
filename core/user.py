import logging
from pathlib import Path


from core import csv_addon, parser, type_helpers
from core.player_data import PlayerData
from core.player_data_models import NormalizedPlayerData

USERS_CSV_PATH = Path(__file__).resolve().parents[1] / "db" / "users.csv"


class UsersVault:
    def __init__(self):
        self.__users = {}

    @property
    def users(self) -> dict:
        return self.__users

    @property
    def keys(self):
        return self.__users.keys()

    def add_user(self, user):
        """Add user to UsersVault

        Args:
            user (User): User object
        """

        self.__users.update({int(user.d_id): user})

    def load_instance_from_csv(self):
        """Instantiate UsersVault from csv

        Raises:
            FileNotFoundError: if csv file not found
        """

        self.__users.clear()
        logging.info("Instantiating from csv")
        self.__load_users__()
        logging.info("Users loaded")

    def save_instance_to_csv(self):
        """Save all authorized users to csv"""

        users_data = []
        for user in self.__users.values():
            users_data.append(self.__generate_user_data__(user))
        csv_addon.write_to_csv(USERS_CSV_PATH, users_data)
        logging.info("All userdata saved")

    def get_user(self, d_id: int):
        """Get user by discord id

        Args:
            d_id (int): user's discord ID

        Returns:
            User: User object
        """

        return self.__users.get(d_id)

    def delete_by_dID(self, d_id: int) -> None:
        """Delete user by his discord ID

        Args:
            d_id (int): user's discord ID
        """

        del self.__users[d_id]

    def is_authorized(self, d_id: int) -> bool:
        """Check if user is authorized

        Args:
            d_id (int): user's discord ID

        Returns:
            bool: True if user is authorized, False otherwise
        """

        return self.__users.get(d_id) is not None

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
