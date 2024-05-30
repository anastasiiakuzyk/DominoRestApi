from fastapi import FastAPI
from routers.board_routes import router as board_router
from routers.auth_routes import router as auth_router
from services.database.database import create_table

app = FastAPI()

app.include_router(board_router)
app.include_router(auth_router, prefix="/auth")

# Initialize the database
create_table()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
