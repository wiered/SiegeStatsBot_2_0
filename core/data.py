from config import Config


class RoleDicts:
    config = Config()
    config.read_roles()

    rank_roles = {
        "nomatchesplayedthisseason": config.unranked,
        "notplayed": config.unranked,
        "unranked": config.unranked,
        "N/A": config.unranked,
        "copper": config.copper,
        "bronze": config.bronze,
        "silver": config.silver,
        "gold": config.gold,
        "platinum": config.platinum,
        "emerald": config.emerald,
        "diamond": config.diamond,
        "champion": config.champion,
    }

    rank_roles_ids = [
        config.unranked,
        config.copper,
        config.bronze,
        config.silver,
        config.silver,
        config.gold,
        config.platinum,
        config.emerald,
        config.diamond,
        config.champion,
    ]

    @staticmethod
    def get_rank_role(rank):
        _rank = rank.lower()
        _rank = _rank.replace(" ", "").replace("-", "")
        for i in range(5):
            _rank = _rank.replace(str(i + 1), "")

        return RoleDicts.rank_roles.get(_rank)
