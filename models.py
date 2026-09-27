from pydantic import BaseModel
class LoginRequest(BaseModel): username:str; password:str
class RegisterRequest(BaseModel): username:str; full_name:str=''; password:str; email:str=''
class ProfileUpdateRequest(BaseModel): full_name:str=''; email:str=''; phone:str=''
class PasswordChangeRequest(BaseModel): current_password:str; new_password:str; confirm_password:str
class PasswordResetRequest(BaseModel): username:str; new_password:str
