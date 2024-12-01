import os
from typing import Literal
from dotenv import load_dotenv
from openai import OpenAI
import CoTTemplate
import json
import functools

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

GPT_3_5_TURBO = "gpt-3.5-turbo"
GPT_4O_MINI = "gpt-4o-mini"
GPT_4O = "gpt-4o"
default_model = GPT_4O_MINI
default_model_type: Literal["openai", "llama"] = "openai"


@functools.lru_cache(maxsize=1)
def get_character_schema():
    from Character import Character

    return Character.get_schema()


@functools.lru_cache(maxsize=1)
def get_event_schema():
    from Character import Event

    return Event.model_json_schema()


@functools.lru_cache(maxsize=1)
def get_weather_schema():
    from World import Weather

    return Weather.model_json_schema()


async def raw_completion_explicit_cot(messages):
    return await raw_completion(CoTTemplate.template_in_message + messages)


async def raw_completion(messages):
    """
    example: messages == [
                {
                    "role": "system",
                    "content": f"You are role-playing as {character1.name}. Respond directly in character, without any explanations or thoughts about what the character would say. Use the following information about the character: {char1_json}",
                },
                {"role": "user", "content": prompt},
            ]
    """
    try:
        response = client.chat.completions.create(
            model=default_model,
            messages=messages,
        )
        content = response.choices[0].message.content.strip()
        with open("chat.log", "a") as log_file:
            log_file.write(content + "\n")
        return content
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return "I'm not sure how to respond to that."


async def chat_sim_one_day(all_character, date: str):
    all_character_json = [char.model_dump_json() for char in all_character]
    from World import World

    weather_schema = get_weather_schema()
    event_schema = get_event_schema()
    messages = [
        {
            "role": "system",
            "content": f"""
Plase chain of thoughts.
You will have data of the characters and simulated days info, please based on \
each character's data, simulate some events happenned for them, events could have multiple \
characters involved, had have interaction with one another if it make sense.
all persons: {all_character_json}
today: {date}
1. For "city" each person in, generate today's weather, weather's schema is {weather_schema}. \
Store the weather of each city in a list, WEATHER_LIST
2. For each character, generate 3 events for them, based on info known and weather in the city. \
Event's schema is {event_schema}, store the events in a list, EVENTS_LIST
4. Return the simulated day in json strictly follows schema: {World.get_schema()}, without any explanations or thoughts.
""",
        },
    ]
    return await raw_completion_explicit_cot(messages)


async def fix_character(user_data_json):
    """
    This method will return a json of data that can be loaded as a Character
    """

    schema = get_character_schema()
    messages = [
        {
            "role": "system",
            "content": f"""
I will give you two json, one is data of a Person potentially in old schema, another is new schema.
1. Please strictly fit the old data into new schema.
2. For the missing attribute in the data, generate some reasonable data according to the person's info.
3. Return the result directly in json, without any explanations or thoughts.
person's data is {user_data_json}
new schema is {schema}
""",
        }
    ]
    return await raw_completion(messages)


async def new_character(note, next_character_id=None):
    char_schema = get_character_schema()
    """
    This method will return a json of data that can be loaded as a Character
    """
    messages = [
        {
            "role": "system",
            "content": f"""
I will give you json a Person schema, please help generate a person for me.
{f"This person's id is {next_character_id}" if next_character_id else ""}\
{note or ""}\
1. Each new person must have more than 3 experiences, 10 events from past couple days.
2. You MUST strictly follow the data schema.
3. Return the result directly in json, without any explanations or thoughts.\
person's schema is {char_schema} \
""",
        }
    ]
    return await raw_completion(messages)


async def world_process_event(event, related_characters, waethers, note=None):
    char_schema = get_character_schema()
    event_schema = get_event_schema()

    messages = [
        {
            "role": "system",
            "content": f"""
Please use Chain of Thoughts and follow these steps carefully:

{note or ""}

1. I will provide you with weather data, a list of important characters involved in an event, and the JSON of the event.

2. Your first task is to EXPAND and MODIFY the event's description:
   - The current description must be extended to approximately 200 words.
   - Incorporate details about the weather and the characters' interactions.
   - Add vivid details and dialogue to make the event more engaging.

3. Create a NEW_EVENT object that strictly follows this Event schema: {event_schema}
   - Copy all fields from the original event.
   - Replace the 'description' field with your expanded version.

Here's the data:
Weather: {json.dumps([w.model_dump() for w in waethers])}
Characters: {json.dumps([c.model_dump() for c in related_characters])}
Original Event: {event.model_dump()}

4. Next, consider the impact of this event on each involved character:
   - 1.5% chance of significant change
   - 4.5% chance of moderate change
   - 74% chance of slight change
   - 20% chance of no change
   - Relationships between characters may also change based on the event.

5. Create NEW_CHARACTERS objects for all involved characters, strictly following this Character schema: {char_schema}
   - Modify character attributes based on the event's impact.
   - Update relationships if applicable.

6. Return the result in this exact JSON format, without any explanations or thoughts:
{{
  "related_characters": [NEW_CHARACTERS],
  "event": NEW_EVENT
}}

Ensure that the NEW_EVENT object has an expanded description and that character changes are reflected in NEW_CHARACTERS.
""",
        }
    ]
    return await raw_completion(messages)
