from fastapi import FastAPI


from app.routes import ServiceRouter

app = FastAPI()

app.include_router(ServiceRouter, prefix="/service", tags=["service"])

@app.get("/ping")
async def pong():
    return {"ping": "pong!"}
