from fastapi import FastAPI, HTTPException, WebSocket
import asyncio
import json
from World import world
from Character import Character
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import datetime
from contextlib import asynccontextmanager
from websocket_service import clients, notifyUpdate
from fastapi import WebSocketDisconnect
from websockets.exceptions import ConnectionClosedError

Character.load_all_characters


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)
scheduler = AsyncIOScheduler()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    await websocket.send_json({"event": "init", "world": world.model_dump()})
    try:
        # Periodically send updates
        while True:
            try:
                message = {"event": "alive", "status": "Event ongoing"}
                await websocket.send_json(message)
                await asyncio.sleep(15)
            except ConnectionClosedError as ce:
                print(f"WebSocket connection closed: {ce}")
                break
            except Exception as e:
                print(f"Error sending message: {str(e)}")
                break
    except WebSocketDisconnect:
        print(f"Client #{id(websocket)} disconnected normally")
    except Exception as e:
        print(f"WebSocket error: {str(e)}, type: {type(e)}")
    finally:
        if websocket in clients:
            clients.remove(websocket)
        print(f"Client #{id(websocket)} connection cleaned up")


@app.post("/interact")
async def interact():
    message = {"event": "interaction", "status": "User interacted"}
    for client in clients:
        await client.send_json(message)
    return {"message": "Interaction sent"}


@app.get("/")
def read_root():
    return world.model_dump()


# simulate a day
@app.get("/test")
async def test():
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
