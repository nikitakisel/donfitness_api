from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.api.endpoints import users
from app.api.endpoints.items import items_get, items_post, items_put, items_delete

from app.config import origins

# FastAPI App
app = FastAPI()

app.add_middleware(
   CORSMiddleware,
   allow_origins=origins,
   allow_credentials=True,  # Important for cookies and sessions
   allow_methods=["*"],      # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
   allow_headers=["*"],      # Allows all headers in the request
)

# Include the Router in Main App
app.include_router(users.router, prefix="/api/v1")
app.include_router(items_get.router, prefix="/api/v1")
app.include_router(items_post.router, prefix="/api/v1")
app.include_router(items_put.router, prefix="/api/v1")
app.include_router(items_delete.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
