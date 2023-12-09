from config import Config

class RoleDicts:
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
        'Champion' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vZTFmYzZlYjItOGM1OS00OTY2LWE0OTgtZjBiMTQ0MDEwMGMw.webp',
        'No rank': 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vZTFmYzZlYjItOGM1OS00OTY2LWE0OTgtZjBiMTQ0MDEwMGMw.webp',
        
        'no matches played this season': 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vMjUyYWRhNjMtNDQzOS00ZmI3LWIzZjktNDY0YWZlNTA3MGY2.webp',
        'not played': 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vMjUyYWRhNjMtNDQzOS00ZmI3LWIzZjktNDY0YWZlNTA3MGY2.webp',
        'unranked' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vMjUyYWRhNjMtNDQzOS00ZmI3LWIzZjktNDY0YWZlNTA3MGY2.webp',
        
        'copper-1' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vNmE5MDg5N2MtYmE4MS00ZDIzLWJkZjAtMDQ3MmI2YjRiOGQ4.webp',    
        'copper-2' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vZjZlODI4MWUtMTljNS00OTM1LTk4NjgtZDllNTE3OGZhOGNi.webp',    
        'copper-3' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vOTdlZTRlZTAtMTNjNy00YzA1LWE0NGYtMDcyNmY2ZmIxOTNl.webp',    
        'copper-4' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vOTdlZTRlZTAtMTNjNy00YzA1LWE0NGYtMDcyNmY2ZmIxOTNl.webp',    
        'copper-5' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vZjdlYWU1YTMtYzAyZi00ODBjLWI2NzUtNTg2MDg0YzM2ZWI0.webp',    

        'bronze-1' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vNDllOTQ2N2MtN2E5Yy00ODA2LWIxNDktMWMwMWQ5OTRkNDNh.webp',    
        'bronze-2' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vYmVkNDVhOTgtMWZmYS00YmNmLTliNDYtMTVlMGE2ZjIyNWJi.webp',    
        'bronze-3' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vNWUwZTQzY2MtYTNjOS00ZTFmLWJiYTUtNzQ4ZDdlMjdjMTFh.webp',    
        'bronze-4' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vYjQzNTI1Y2YtYTJiMS00MDQ2LWIyYjctY2YyMmExYzU2YjZl.webp',    
        'bronze-5' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vN2ZhNzZmZGYtZjZmNC00MzZhLWI2MDgtNzVmZDA4NzM3MGUx.webp',    

        'silver-1' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vNGJjOWM5MmQtYTJiMS00ODA4LWIxZjEtMTBmZDFiMThjM2Ux.webp',    
        'silver-2' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vZjcxNGZlNTYtMTZiOC00ZWFkLTk0N2QtY2E0YzQ0N2VhMDFj.webp',    
        'silver-3' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vZjkwYjVjMzItNWVhNy00YWFmLWFlMzYtYzVkMGQxMDEzOGRi.webp',    
        'silver-4' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vMGI1ZDkwZjYtZDUyOS00MDUzLWI3ZGEtZDI1ZmE3MDIwNmFk.webp',    
        'silver-5' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vZTc3MzY1NjEtZDFhMy00YmRiLThjMmMtZTUxMWY2YjM0NzAx.webp',    

        'gold-1' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vNGZlZGEwOGQtNjVlOC00NWY3LTg4OGYtMGVkYTcyZDdmMGMw.webp',    
        'gold-2' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vNTE2MjRjOWEtYmY1YS00MjlkLTkzMzAtZWJkNWJhYzgyMTEz.webp',    
        'gold-3' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vYjU1MmZhNmItODcwNC00NjYzLWFhMDctYjIyOWRhNDRlYzkx.webp',     
        'gold-4' : 'https://img.apitab.com/plain/quality:50/resize:fit:256:0/bG9jYWw6Ly8vOTg1MjlhMjAtOTgwMy00ZDRiLTljMmMtYWY2ZjI5MTUyYzEy.webp',     
        'gold-5' : 'https://img.apitab.com/plain/quality:50/resize:fit:256:0/bG9jYWw6Ly8vMGUwNjU2OWItMjg3My00OGY2LThlMDktZGQzNzAwNWI1YTdl.webp',     

        'platinum-1' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vODQxZjViM2YtYTI2ZC00NWI5LWE3N2EtYTg4MjljNzMxMDFj.webp',    
        'platinum-2' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vZDAxZmRmMzItNWMwYS00M2ZkLTlkMzUtMTM2NzdiMjJlZGNi.webp',    
        'platinum-3' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vZGE5YWNjZGQtZTA3Yi00OTk0LTkwNDgtNGE0ZDkyZTg4ZWU1.webp',    
        '-platinum-4' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vZGE5YWNjZGQtZTA3Yi00OTk0LTkwNDgtNGE0ZDkyZTg4ZWU1.webp',    
        'platinum-5' : 'https://img.apitab.com/plain/quality:50/resize:fit:256:0/bG9jYWw6Ly8vZDVmMTc4NmMtMzlkMS00MDU0LTk3NjktM2RhYTFjNmU1OGQx.webp',    

        'emerald-1' : 'https://img.apitab.com/plain/quality:50/resize:fit:256:0/bG9jYWw6Ly8vMDg5ZTRhMTktYzNkNi00NmE0LWJlMzQtZjNkYTkwNGRkNDVk.webp',    
        '-emerald-2' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vZDAxZmRmMzItNWMwYS00M2ZkLTlkMzUtMTM2NzdiMjJlZGNi.webp',    
        '-emerald-3' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vZGE5YWNjZGQtZTA3Yi00OTk0LTkwNDgtNGE0ZDkyZTg4ZWU1.webp',    
        '-emerald-4' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vZGE5YWNjZGQtZTA3Yi00OTk0LTkwNDgtNGE0ZDkyZTg4ZWU1.webp',    
        '-emerald-5' : 'https://img.apitab.com/plain/quality:50/resize:fit:256:0/bG9jYWw6Ly8vZDVmMTc4NmMtMzlkMS00MDU0LTk3NjktM2RhYTFjNmU1OGQx.webp',    

        'diamond-1' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vNGI3YmJhZTgtZTcyMC00ZTg3LWFjNjQtM2NlNmZiODUxYjJk.webp',    
        'diamond-2' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vZGIyZmIzY2YtYTg4Yi00ODc2LWEyMjctYjBiMzZmYWI5MDg2.webp',    
        'diamond-3' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vZDI1MGJiNjgtYTJiNS00YTg5LTllZjYtYzlhM2MyZDc5NGNl.webp',
        '-diamond-4' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vZDI1MGJiNjgtYTJiNS00YTg5LTllZjYtYzlhM2MyZDc5NGNl.webp',
        '-diamond-5' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vZDI1MGJiNjgtYTJiNS00YTg5LTllZjYtYzlhM2MyZDc5NGNl.webp',
        
        'champion' : 'https://img.apitab.com/plain/quality:50/resize:fit:0:250/bG9jYWw6Ly8vZTFmYzZlYjItOGM1OS00OTY2LWE0OTgtZjBiMTQ0MDEwMGMw.webp',  
    }
    
    config = Config()
    config.read_roles()
    
    rank_roles = {
        'nomatchesplayedthisseason': config.unranked,
        'notplayed': config.unranked,
        'unranked' : config.unranked,
        'N/A'      : config.unranked,
        
        'copper'   : config.copper,
        'bronze'   : config.bronze,
        'silver'   : config.silver,
        'gold'   : config.gold,
        'platinum'   : config.platinum,
        'emerald' : config.emerald,
        'diamond'   : config.diamond,
        'Champion' : config.champion,
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
        _rank = _rank.replace(' ', '').replace('-', '')
        for i in range(5):
            _rank = _rank.replace(str(i+1), '')
        
        return RoleDicts.rank_roles.get(_rank)
    