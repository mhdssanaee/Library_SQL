from storageManager import StorageManager
from models import User
import hashlib
import re
from datetime import datetime


class AuthService:
    def __init__(self, storage_manager: StorageManager):
        self.storage = storage_manager

    def _hash_password(self, password):
            return hashlib.sha256(password.encode()).hexdigest()

    def _is_valid_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def register(self,first_name, last_name, email, password):
        
        if not self._is_valid_email(email):
            print("Invalid email format.")
            return False
        existing_user = self.storage.get_user_by_email(email)
        if existing_user:
            print("User already exists.")
            return False
        hashed_password = self._hash_password(password)
        new_user = User(first_name, last_name, email.lower(), hashed_password)
        self.storage.add_user(new_user)
        print(f"User {new_user.first_name} {new_user.last_name} registered successfully")
        return True


        
        

    def login_user(self,email, password):
        user = self.storage.get_user_by_email(email)
        if not user:
            print("User not found. Register first.")
            return None
        if user.password != self._hash_password(password):
            print("Incorrect password. Please try again.")
            return None
        if user.is_banned:
            print("User is banned.")
            return None
        user.last_login = datetime.now()
        self.storage.update_user_status(user.email,user.negative_score,user.is_banned,user.last_login)
        print(f"User {user.first_name} {user.last_name} logged in successfully")
        return user            
