from __future__ import annotations
from pydantic import BaseModel, Field
import json
import os
from typing import List, Dict, Any
from Character import Event, Character
from datetime import datetime, timedelta
from chat import chat_sim_one_day, world_process_event
import asyncio
import time
from websocket_service import notifyUpdate


class Weather(BaseModel):
    city_name: str
    weather: str


class World(BaseModel):
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    events: List[Event]
    weathers: List[Weather]

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        return cls.model_json_schema()

    @classmethod
    def load_from_local(cls) -> World:
        file_path = "world.json"
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"World file not found: {file_path}")

        with open(file_path, "r") as f:
            data = json.load(f)
            return cls(**data)

    @classmethod
    def load_from_json_str(cls, json_str) -> World:
        return cls(**json.loads(json_str))

    def advance_date(self) -> None:
        """
        Move the date forward by one day.
        """
        current_date = datetime.strptime(self.date, "%Y-%m-%d")
        next_date = current_date + timedelta(days=1)
        self.date = next_date.strftime("%Y-%m-%d")

    def save(self) -> None:
        file_path = f"world.json"
        with open(file_path, "w") as f:
            json.dump(self.model_dump(), f, indent=2)

    def get_current_date(self) -> str:
        """
        Get the current date of the world.

        Returns:
            str: The current date in 'YYYY-MM-DD' format.
        """
        return self.date

    async def sim_one_day(self):
        start_time = time.time()
        all_characters = await Character.get_all_characters()
        self.advance_date()
        current_date = self.get_current_date()
        response = await chat_sim_one_day(all_characters, f"date: {current_date}")

        today_log_file = f"{current_date}.log"
        with open(today_log_file, "a") as f:
            f.write(f"responses from chat_sim_one_day:\n{response}\n\n")
        self = World.load_from_json_str(response)
        self.events = await self.process_event()
        self.save()
        notifyUpdate("World", None, self.model_dump())
        end_time = time.time()
        execution_time = end_time - start_time

        # Log the execution time
        with open(today_log_file, "a") as log_file:
            log_file.write(
                f"[{datetime.now()}] sim_one_day execution time: {execution_time:.2f} seconds\n"
            )
        return {"date": current_date, "world": self.model_dump()}

    async def process_event(self, note=None):
        today_log_file = f"{self.get_current_date()}.log"
        new_event = []
        with open(today_log_file, "a") as f:
            f.write(f"Started processing events...\n")
            for event in self.events:
                character_ids = event.id_of_character_involved
                related_characters = await asyncio.gather(
                    *[Character.get_character(c_id) for c_id in character_ids]
                )
                response = await world_process_event(
                    event, related_characters, self.weathers, note
                )

                f.write(f"responses from world_process_event:\n{response}\n\n")
                # store back changed characters
                response = json.loads(response)
                for cj in response["related_characters"]:
                    char = Character(**cj)
                    char.save()
                    notifyUpdate("Character", char.basic_info.id, char.model_dump())
                new_event.append(Event(**response["event"]))
            f.write(f"Finished processing events.\n")
        return new_event


world = World.load_from_local()
