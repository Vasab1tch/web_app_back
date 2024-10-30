from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, images
from app.database import engine, create_db
from app.models import Base
import uvicorn
app = FastAPI()

# Додати CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await create_db()



# Роутери
app.include_router(auth.router)
app.include_router(images.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)