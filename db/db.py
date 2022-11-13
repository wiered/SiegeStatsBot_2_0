from core.user import UsersVault


class Data:
    def __init__(self):
        self.users_vault = UsersVault()
    
    
    def get_users_vault(self):
        return self.users_vault
    
    
    def get_user(self, d_id):
        print("User id: ", d_id)
        print("User requested: ", self.users_vault.users)
        print("Users keys: ", self.users_vault.users.keys())
        print("Users keys: ", self.users_vault.keys)
        return self.users_vault.get_user(d_id)
    
    
    def add_user(self, user):
        self.users_vault.add_user(user)
        print("User added: ", self.users_vault.users)
        

users_db = UsersVault()