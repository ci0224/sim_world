from fastapi import FastAPI, HTTPException
import json
from World import World
from Character import Character
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import datetime
from contextlib import asynccontextmanager


Character.load_all_characters


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)
scheduler = AsyncIOScheduler()


@app.get("/")
def read_root():
    world = World.load_from_local()
    return world.model_dump()


@app.get("/test")
async def test():
    world = World.load_from_local()
    response = await world.sim_one_day()
    return json.dumps(response)


async def scheduled_test():
    print(f"Running scheduled test at {datetime.now()}")
    await test()


@app.get("/introduce_new_character")
async def test2():
    c = await Character.create_new_character(
        "A Chinese international senior student at UC Davis, living in "
        + "Davis, California, who loves to drink but gets drunk after even one beer."
    )
    return {"test": c.model_dump()}


@app.get("/char/{id}")
async def check_character(id: int):
    try:
        character = await Character.load_from_json(id)
        return character.model_dump()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Character with id {id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.on_event("startup")
async def startup_event():
    scheduler.add_job(
        scheduled_test, CronTrigger(hour=0, minute=0)
    )  # Run every day at midnight
    scheduler.start()


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
