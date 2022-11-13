class RoleDicts:
    roles_Ids = {
        "No matches played this season": 869077141281718403,
        None       : 869077141281718403,
        "unranked" : 869077141281718403,
        "copper"   : 865376407214751778,
        "bronze"   : 865377980636069889,
        "silver"   : 865378800694853634,
        "gold"     : 865379412358070288,
        "platinum" : 865379469267042314,
        "diamond"  : 865379593950724116,
        "champion" : 865379707428405279
    }

    ranks_pics = {
        'No matches played this season': 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vMjUyYWRhNjMtNDQzOS00ZmI3LWIzZjktNDY0YWZlNTA3MGY2.webp',
        'Not played': 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vMjUyYWRhNjMtNDQzOS00ZmI3LWIzZjktNDY0YWZlNTA3MGY2.webp',
        'Unranked' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vMjUyYWRhNjMtNDQzOS00ZmI3LWIzZjktNDY0YWZlNTA3MGY2.webp',
        'N/A'      : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vMjUyYWRhNjMtNDQzOS00ZmI3LWIzZjktNDY0YWZlNTA3MGY2.webp',
        'Copper'   : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vNmE5MDg5N2MtYmE4MS00ZDIzLWJkZjAtMDQ3MmI2YjRiOGQ4.webp',
        'Bronze'   : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vNDllOTQ2N2MtN2E5Yy00ODA2LWIxNDktMWMwMWQ5OTRkNDNh.webp',
        'Silver'   : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vNGJjOWM5MmQtYTJiMS00ODA4LWIxZjEtMTBmZDFiMThjM2Ux.webp',
        'Gold'     : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vNGZlZGEwOGQtNjVlOC00NWY3LTg4OGYtMGVkYTcyZDdmMGMw.webp',
        'Platinum' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vODQxZjViM2YtYTI2ZC00NWI5LWE3N2EtYTg4MjljNzMxMDFj.webp',
        'Diamond'  : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vNGI3YmJhZTgtZTcyMC00ZTg3LWFjNjQtM2NlNmZiODUxYjJk.webp',
        'Champion' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vZTFmYzZlYjItOGM1OS00OTY2LWE0OTgtZjBiMTQ0MDEwMGMw.webp'
    }

    Ranks_with_nums = {
            "": "Not played",
            "unranked": "Unranked",
            "copper-1": "Copper",
            "copper-2": "Copper",
            "copper-3": "Copper",
            "copper-4": "Copper",
            "copper-5": "Copper",
            "bronze-1": "Bronze",
            "bronze-2": "Bronze",
            "bronze-3": "Bronze",
            "bronze-4": "Bronze",
            "bronze-5": "Bronze",
            "silver-1": "Silver",
            "silver-2": "Silver",
            "silver-3": "Silver",
            "silver-4": "Silver",
            "silver-5": "Silver",
            "gold-1": "Gold",
            "gold-2": "Gold",
            "gold-3": "Gold",
            "gold-4": "Gold",
            "gold-5": "Gold",
            "platinum-1": "Platinum",
            "platinum-2": "Platinum",
            "platinum-3": "Platinum",
            "diamond-1": "Diamond",
            "diamond-2": "Diamond",
            "diamond-3": "Diamond",
            "champion": "Champion"
        }

    ranks = [
        "No matches played this season", 
        "unranked", 
        "copper", 
        "bronze", 
        "silver", 
        "gold", 
        "platinum", 
        "diamond", 
        "champion"
        ]


class BotStdMsgs:
    unauthorized_msg = """Для авторизации напишите `w!auth <r6 name>`. После свою статистику можно получить с помошью `w!stats`
    Если хотите посмотреть чужую статистику - `w!stats <r6 name> or <user tag>`
    """

    authorized_msg = """Вы уже авторизированы
    ```w!stats     to show your stats
    w!stats [siege name] or [user tag]     to show others stats```
    """

    help_msg = """
    ```
    Rainbow Six Stats:
    w!auth [username]                       Авторизация в боте
    w!stats [username or discord tag]       Показать статистику в боте

    Party Find:
    w!party [quantity]                      Создать объявление о поиске пати
    w!lock                                  Создать приватный голосовой канал для всех, 
                                                кто сейчас в голосовом канале вместе с вами
    ```
    """
    
    
class APIUrls:
    # api urls
    tabstats_search_api_url = "https://r6.apitab.net/website/search"
    tabstats_profie_api_url = "https://r6.apitab.net/website/profiles/{}"

    # profile url
    tabstats_profie_url = "https://tabstats.com/siege/player/{}/{}"