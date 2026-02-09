import database as _database
import models as _models
import sqlalchemy.orm as _orm
import schemas as _schemas
import email_validator as _email_validator
import fastapi as _fastapi
import bcrypt  # Changed from passlib.hash
from jose import jwt as _jwt # type: ignore
import fastapi.security as _security
import os
from datetime import datetime, timedelta

_JWT_SECRET = os.getenv("JWT_SECRET")
if not _JWT_SECRET:
    raise RuntimeError("JWT_SECRET is not set")

oauth2Schema = _security.OAuth2PasswordBearer(tokenUrl="/api/v1/login")

def create_db():
    return _database.Base.metadata.create_all(bind=_database.engine)

def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
async def getUserByEmail(email: str, db: _orm.Session):
    return db.query(_models.UserModel).filter(_models.UserModel.email == email).first()

async def create_user(user: _schemas.UserRequest, db: _orm.Session):
    # Check for email validation
    try:
        isValid = _email_validator.validate_email(user.email)
        email = isValid.email
    
    except _email_validator.EmailNotValidError:
        raise _fastapi.HTTPException(status_code=400, detail="Provide valid email")
    
    # Convert user password to hash using bcrypt directly
    password_bytes = user.password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    
    # Create user models to be saved in database
    user_obj = _models.UserModel(
        email=email,
        name=user.name,
        phone=user.phone,
        password_hash=hashed_password.decode('utf-8'),  # Store as string
    )   
        
    # Save the user in the db
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj
    
# async def create_token(user: _models.UserModel):
#     # Convert user models to user schemas
#     user_schema = _schemas.UserResponse.from_orm(user)
#     print(user_schema)
    
#     # Convert obj to dictionary
#     user_dict = user_schema.dict()
#     del user_dict["created_at"]
    
#     token = _jwt.encode(user_dict, _JWT_SECRET)
#     return dict(access_token=token, token_type="bearer")

async def create_token(user: _models.UserModel):
    # Convert user models to user schemas
    user_schema = _schemas.UserResponse.from_orm(user)
    print(user_schema)
    # Convert obj to dictionary
    user_dict = user_schema.dict()
    del user_dict["created_at"]

    expire = datetime.utcnow() + timedelta(hours=24)
    payload = {
        "sub": user.id,
        "exp": expire
    }
    user_dict.update({"exp": expire})

    token = _jwt.encode(payload, _JWT_SECRET, algorithm="HS256")
    return {
        "access_token": token,
        "token_type": "bearer"
    }



async def login(email: str, password: str, db = _orm.Session):
    db_user = await getUserByEmail(email = email, db=db)
    
    #return false if not user with email found
    if not db_user:
        return False
    #return false if no user with password found
    if not db_user.password_verification(password = password):
        return False
    
    return db_user


# async def current_user(db: _orm.Session = _fastapi.Depends(get_db), token: str = _fastapi.Depends(oauth2Schema)):
#     try:
#          payload = _jwt.decode(token, _JWT_SECRET, algorithms=['HS256'])
#          #Get user by id, which is available in the decoded paylod
#          db_user = db.query(_models.UserModel).get(payload["id"])
#     except:
#         raise _fastapi.HTTPException(status_code= 401, detail="Wrong Credentials")
async def current_user(
    db: _orm.Session = _fastapi.Depends(get_db),
    token: str = _fastapi.Depends(oauth2Schema)
):
    try:
        payload = _jwt.decode(token, _JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")

        if not user_id:
            raise _fastapi.HTTPException(status_code=401, detail="Invalid token")

        db_user = db.query(_models.UserModel).get(user_id)

        if not db_user:
            raise _fastapi.HTTPException(status_code=401, detail="User not found")

        return _schemas.UserResponse.from_orm(db_user)

    except _jwt.ExpiredSignatureError:
        raise _fastapi.HTTPException(status_code=401, detail="Token expired")
    except _jwt.InvalidTokenError:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid token")

# async def current_user(
#     db: _orm.Session = _fastapi.Depends(get_db),
#     token: str = _fastapi.Depends(oauth2Schema)
# ):
#     try:
#         payload = _jwt.decode(token, _JWT_SECRET, algorithms=["HS256"])
#         user_id = payload.get("sub")

#         if not user_id:
#             raise _fastapi.HTTPException(status_code=401, detail="Invalid token")

#         db_user = db.query(_models.UserModel).get(user_id)

#         if not db_user:
#             raise _fastapi.HTTPException(status_code=401, detail="User not found")

#         return _schemas.UserResponse.from_orm(db_user)

#     except _jwt.ExpiredSignatureError:
#         raise _fastapi.HTTPException(status_code=401, detail="Token expired")
#     except _jwt.InvalidTokenError:
#         raise _fastapi.HTTPException(status_code=401, detail="Invalid token")
    
    #if all is okay, then return the DTO/Schema version User
    # return _schemas.UserResponse.from_orm(db_user)
        

async def create_post(user: _schemas.UserResponse, post: _schemas.PostRequest, db: _orm.Session):
    post = _models.PostModel(
        **post.dict(), 
        user_id = user.id,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    #convert the post model to Post DTO/schema and return to API layer 
    return _schemas.PostResponse.from_orm(post) 

async def get_posts_by_user(user: _schemas.UserResponse, db: _orm.Session):
    posts = db.query(_models.PostModel).filter_by(user_id = user.id)
    #convert each post model to post schema and make a list to be returned
    return list(map(_schemas.PostResponse.from_orm, posts))

async def get_posts_by_all( db: _orm.Session):
    posts = db.query(_models.PostModel)
    #convert each post model to post schema and make a list to be returned
    return list(map(_schemas.PostResponse.from_orm, posts))

async def get_post_detail(post_id: int, db: _orm.Session):
    db_post = db.query(_models.PostModel).filter(_models.PostModel.id == post_id).first()
    if  db_post is None:
        raise _fastapi.HTTPException(status_code=404, detail="Post not found")
    # return _schemas.PostResponse.from_orm(db_post)
    return db_post

async def get_user_detail(user_id: int, db: _orm.Session):
    db_user = db.query(_models.UserModel).filter(_models.UserModel.id == user_id).first()
    if  db_user is None:
        raise _fastapi.HTTPException(status_code=404, detail="User not found")
    return _schemas.UserResponse.from_orm(db_user)
    # return db_user

async def delete_post(post: _models.PostModel, db: _orm.Session):
    db.delete(post)
    db.commit()
    # return True
    
async def update_post(
    post: _models.PostModel, post_request: _schemas.PostRequest, db: _orm.Session
):
    post.post_title = post_request.post_title
    post.post_description = post_request.post_description
    post.image = post_request.image
    db.commit()
    db.refresh(post)
    return _schemas.PostResponse.from_orm(post)
# create_db()