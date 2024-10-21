from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import random
import asyncio
import json
from datetime import datetime
import os
from World import World
from Character import Character
from chat import generate_ai_response


Character.load_all_characters
world = World.load_from_local()

app = FastAPI()


# 定义交互结果模型
class InteractionResult(BaseModel):
    character1: str
    character2: str
    message: str
    response: str


def load_interaction_history():
    if os.path.exists("interaction_history.json"):
        with open("interaction_history.json", "r") as f:
            return json.load(f)
    return []


def save_interaction_history(interactions):
    with open("interaction_history.json", "w") as f:
        json.dump(interactions, f, indent=2)


async def run_daily_interactions():
    interactions = []
    all_characters = await Character.get_all_characters()
    for _ in range(3):  # 每天进行5次交互
        char1, char2 = random.sample(all_characters, 2)

        message_prompt = f"Generate a casual greeting or question from {char1.name} to {char2.name}, considering their personalities and backgrounds."
        message = await generate_ai_response(message_prompt, char1, char2)

        response_prompt = f"{char1.name} just said: '{message}'. Generate a suitable response from {char2.name}, considering their personality and background."
        response = await generate_ai_response(response_prompt, char2, char1)

        interaction = InteractionResult(
            character1=char1.name,
            character2=char2.name,
            message=message,
            response=response,
        )
        interactions.append(interaction.model_dump())
        await asyncio.sleep(1)  # 模拟交互延迟

    history = load_interaction_history()
    today = datetime.now().strftime("%Y-%m-%d")
    history.append({"date": today, "interactions": interactions})
    save_interaction_history(history)

    print("Daily interactions completed and saved.")


def get_history_response():
    history = load_interaction_history()
    return {"history": history}


@app.get("/")
def read_root():
    return get_history_response()


@app.get("/interaction-history")
def get_interaction_history():
    return get_history_response()


@app.get("/test")
async def test():
    response = await world.sim_one_day()
    return json.dumps(response)


@app.get("/introduce_new")
async def test2():
    c = await Character.create_new_character(
        "A Chinese international senior student in ucdavis, living in Davis"
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


@app.get("/daily-interactions")
async def trigger_daily_interactions(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_daily_interactions)
    return {"message": "Daily interactions triggered"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
