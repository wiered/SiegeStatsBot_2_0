__user_str = "| {:2} | {:15} | {:3} | {:10} |"

__s1 = "-"*2
__s2 = "-"*15
__s3 = "-"*3
__s4 = "-"*10 

__separator = f"+-{__s1}---{__s2}---{__s3}---{__s4}\b  "

def cout(user, search_request: str = ""):
    if isinstance(user, list):
        cout_users(user, search_request)
    if isinstance(user, dict):
        cout_user(user)


def cout_users(users_list, search_request):
    if not search_request:
        print("No search request")
        return
    
    __print_header(search_request)
    i = 1
    for user in users_list:
        print(__user_str.format(str(i), user["name"], user["level"], user["rank"]))
        i+=1
    print(__separator)

def cout_user(user):
    __print_header(user["name"])
    print(__user_str.format(0, user["name"], user["level"], user["rank"]))
    print(__separator)

def __print_header(name):
    print("\n\nSearch results for: {}".format(name))
    print(f"   {__s1}---{__s2}---{__s3}---{__s4}+")
    print(__user_str.format("№", "Name", "Lvl", "Rank"))
    print(f"|-{__s1}-|-{__s2}-|-{__s3}-|-{__s4}-|")
    
    

""" Table example:
Search results for: PePe
   ---------------------------------------+
| №  | Name            | Lvl | Rank       |
|----|-----------------|-----|------------|
| 1  | pepe            |   0 | unranked   |
| 2  | Pepe_           |   0 | N/A        |
| 3  | pepe__          |   0 | N/A        |
| 4  | PEPE____        |   0 | N/A        |
| 5  | pepe_____       |   0 | N/A        |
| 6  | Pepe______      | 104 | N/A        |
| 7  | PEPE________    | 189 | platinum-3 |
| 8  | Pepe___05       |   6 | N/A        |
| 9  | iSaavage_       | 103 | gold-3     |
| 10 | Theguywhohappy  | 150 | N/A        |
| 11 | IM_AUSPICIOUS   | 242 | unranked   |
| 12 | A_Large_Frog    | 225 | N/A        |
+---------------------------------------
"""