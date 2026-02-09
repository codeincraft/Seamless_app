import pydantic as _pydantic
import datetime as _datetime

class UserBase(_pydantic.BaseModel):
    email: str
    name: str
    phone: str
    
class UserRequest(UserBase):
    password: str  # ✅ Fixed: Added colon for type annotation
    
    class Config:  # ✅ Fixed: Capital 'C'
        from_attributes = True  # ✅ Fixed: Pydantic v2 uses from_attributes instead of orm_mode
    
    
class UserResponse(UserBase):
    id: int
    created_at: _datetime.datetime
    
    class Config:  # ✅ Fixed: Capital 'C'
        from_attributes = True  # ✅ Fixed: Pydantic v2 uses from_attributes instead of orm_mode
        
class PostBase(_pydantic.BaseModel):
    post_title: str
    post_description: str
    image: str
    
class PostRequest(PostBase):
    pass

class PostResponse(PostBase):
    id: int  # ✅ Fixed: Added colon for type annotation
    user_id: int  # ✅ Fixed: Added colon for type annotation
    created_at: _datetime.datetime  # ✅ Fixed: Added colon for type annotation
    
    class Config:
        from_attributes = True  # ✅ Fixed: Pydantic v2 uses from_attributes instead of orm_mode