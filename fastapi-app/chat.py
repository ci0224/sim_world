import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

default_model = "gpt-3.5-turbo"


async def generate_ai_response(prompt, character1, character2):
    try:
        char1_json = json.dumps(character1.__dict__)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"You are role-playing as {character1.name}. Respond directly in character, without any explanations or thoughts about what the character would say. Use the following information about the character: {char1_json}",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return "I'm not sure how to respond to that."


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
            model="gpt-3.5-turbo",
            messages=messages,
        )
        content = response.choices[0].message.content.strip()
        with open("chat.log", "a") as log_file:
            log_file.write(content + "\n")
        return content
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return "I'm not sure how to respond to that."


async def sim_one_day(all_character, date: str):
    all_character_json = [char.model_dump_json() for char in all_character]
    messages = [
        {
            "role": "system",
            "content": f"""
You will have data about person and simulated days info, please based on \
each person's data, simulate a day for them, not necessary have interaction with one another \
if it make sense. \
persons: {all_character_json} \
today:{date} \
1. For "city" each person in, generate today's weather \
2. Every person has 3-10 events, based on plan, goal, status, \
weather in the city. \
3. People will communicate with friends, family, coworkers, or strangers, and \
these are not events unless it is really funny or hurts their feelings. \
3. Return the simulated day in json strictly follows
{{
"date":today,
"weather":[{{city_name: weather_in_stort_string }},...],
"events":[{{
"participent":[id_person_involved,...]
"type":"work"|"education"|"volunteer"|"random"
"start_time": like_10:29
"end_time": like_19:29
"description": "string_len_close_to_300"
}},...]
}}
""",
        },
    ]
    return await raw_completion(messages)


async def fix_character(user_data_json):
    """
    This method will return a json of data that can be loaded as a Character
    """

    from Character import Character

    schema = Character.get_schema()
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
    from Character import Character

    schema = Character.get_schema()
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
person's schema is {schema} \
""",
        }
    ]
    return await raw_completion(messages)
