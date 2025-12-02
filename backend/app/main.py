from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database.database import engine
from .models import user, credit
from .routes import auth, users, credit

user.Base.metadata.create_all(bind=engine)
credit.Base.metadata.create_all(bind=engine)

app = FastAPI(title="TrustFlow", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роуты
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(credit.router, prefix="/api/credit", tags=["credit"])

@app.get("/")
async def root():
    return {"message": "TrustFlow Credit Platform API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}