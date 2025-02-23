from fastapi import FastAPI
from apis.routes import router
import uvicorn

#app = FastAPI()
app = FastAPI()

# Include the main API router
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)