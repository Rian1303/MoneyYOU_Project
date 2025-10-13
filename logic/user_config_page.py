#EM DESENVOLVIMENTO
import firebase_admin
from firebase_admin import credentials, firestore

class User_Config_Page:
    def __init__(self):
        pass

    def update_config(self, config_dict):
        # Implement the logic to update user config in Firestore here
        # For example:
        # db = firestore.client()
        # db.collection('users').document(self.user_id).update(config_dict)
        pass

    def ChangeUsername(self, new_username):
        self.update_config({"username": new_username})

    def ChangeEmail(self, new_email):
        self.update_config({"email": new_email})

    def ChangePassword(self, new_password):
        self.update_config({"password": new_password})
