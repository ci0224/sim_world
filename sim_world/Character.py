from __future__ import annotations
from pydantic import BaseModel, Field, ValidationError
from enum import Enum
import json
import os
from typing import List, Optional, Dict, Any
from chat import fix_character, new_character
import util


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non-binary"


class Personality(str, Enum):
    INTJ = "INTJ"
    INTP = "INTP"
    ENTJ = "ENTJ"
    ENTP = "ENTP"
    INFJ = "INFJ"
    INFP = "INFP"
    ENFJ = "ENFJ"
    ENFP = "ENFP"
    ISTJ = "ISTJ"
    ISFJ = "ISFJ"
    ESTJ = "ESTJ"
    ESFJ = "ESFJ"
    ISTP = "ISTP"
    ISFP = "ISFP"
    ESTP = "ESTP"
    ESFP = "ESFP"


class ZodiacSign(str, Enum):
    ARIES = "Aries"
    TAURUS = "Taurus"
    GEMINI = "Gemini"
    CANCER = "Cancer"
    LEO = "Leo"
    VIRGO = "Virgo"
    LIBRA = "Libra"
    SCORPIO = "Scorpio"
    SAGITTARIUS = "Sagittarius"
    CAPRICORN = "Capricorn"
    AQUARIUS = "Aquarius"
    PISCES = "Pisces"


class Experience(BaseModel):
    type: str  # e.g., "work", "education", "volunteer"
    organization: Optional[str] = None
    role: Optional[str] = None
    start_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    end_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    description: str


class Event(BaseModel):
    id_of_character_involved: List[int]
    location: Optional[str] = None
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    end_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    description: str


class BasicInfo(BaseModel):
    id: int
    name: str
    gender: Gender
    birthday: str
    age: int
    nationality: str
    ethnicity: str
    city: str
    home_city: str
    native_language: str
    other_languages: List[str]
    Zodiac_sign: ZodiacSign


class PersonalityAndPsychology(BaseModel):
    personality: Personality
    iq: int
    eq: int
    introvert_extrovert_scale: int = Field(..., ge=0, le=100)
    optimism_pessimism_scale: int = Field(..., ge=0, le=100)
    risk_taking_scale: int = Field(..., ge=0, le=100)
    emotional_stability: int = Field(..., ge=0, le=100)
    openness_to_experience: int = Field(..., ge=0, le=100)
    conscientiousness: int = Field(..., ge=0, le=100)
    agreeableness: int = Field(..., ge=0, le=100)
    neuroticism: int = Field(..., ge=0, le=100)


class EducationAndCareer(BaseModel):
    current_occupation: str
    highest_education_level: str
    salary_in_usd: int


class PhysicalAttributes(BaseModel):
    height_in_cm: float
    weight_in_kg: float
    eye_color: str
    hair_color: str
    skin_tone: str


class PersonalLife(BaseModel):
    relationship_status: str
    sexual_orientation: str
    religion: str
    political_views: str
    hobbies: list[str]
    rent_in_usd: int


class Preferences(BaseModel):
    favorite_color: str
    favorite_food: str
    favorite_movie: str
    favorite_book: str
    favorite_music_genre: str
    favorite_sport: str
    pet_preference: str


class SkillsAndAbilities(BaseModel):
    leadership: int = Field(..., ge=0, le=100)
    communication: int = Field(..., ge=0, le=100)
    problem_solving: int = Field(..., ge=0, le=100)
    creativity: int = Field(..., ge=0, le=100)
    adaptability: int = Field(..., ge=0, le=100)
    stress_management: int = Field(..., ge=0, le=100)
    work_ethic: int = Field(..., ge=0, le=100)
    time_management: int = Field(..., ge=0, le=100)
    financial_management: int = Field(..., ge=0, le=100)
    tech_savviness: int = Field(..., ge=0, le=100)
    patience: int = Field(..., ge=0, le=100)
    travel_experience: int = Field(..., ge=0, le=100)


class CharacterStore:
    _all_characters: Dict[int, "Character"] = {}


class Character(BaseModel):
    basic_info: BasicInfo
    personality_and_psychology: PersonalityAndPsychology
    education_and_career: EducationAndCareer
    physical_attributes: PhysicalAttributes
    personal_life: PersonalLife
    preferences: Preferences
    skills_and_abilities: SkillsAndAbilities
    experiences: List[Experience]
    events_latest_10: List[Event]
    highlight_3_max: List[Event]
    lowlight_3_max: List[Event]

    def save(self):
        os.makedirs("characters", exist_ok=True)
        file_path = f"characters/{self.basic_info.id}.json"

        with open(file_path, "w") as f:
            json.dump(self.model_dump(), f, indent=2)

        if CharacterStore._all_characters is not None:
            CharacterStore._all_characters[self.basic_info.id] = self

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        return cls.model_json_schema()

    @classmethod
    async def load_from_json(cls, character_id: int):
        file_path = f"characters/{character_id}.json"
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Character file not found: {file_path}")

        with open(file_path, "r") as f:
            data = json.load(f)

        try:
            return cls(**data)
        except ValidationError:
            print(
                f"Validation error occurred for character {character_id}. Attempting to fix with chat..."
            )

            fixed_data = await cls.fix_with_chat(json.dumps(data))
            character = cls(**json.loads(fixed_data))
            character.save()
            return character

    @classmethod
    async def fix_with_chat(cls, user_data_json):
        result = util.extract_longest_json(await fix_character(user_data_json))
        print(result)
        return result

    @classmethod
    async def load_all_characters(cls):
        characters_dir = "characters"
        if not os.path.exists(characters_dir):
            print(
                f"Warning: {characters_dir} directory not found. No characters loaded."
            )
            return

        for filename in os.listdir(characters_dir):
            if filename.endswith(".json"):
                character_id = int(filename.split(".")[0])
                character = await cls.load_from_json(character_id)
                if character:
                    CharacterStore._all_characters[character_id] = character

        print(f"Loaded {len(CharacterStore._all_characters)} characters.")

    @classmethod
    async def get_character(cls, character_id: int):
        if not CharacterStore._all_characters:
            await cls.load_all_characters()
        return CharacterStore._all_characters.get(character_id)

    @classmethod
    async def get_all_characters(cls) -> List["Character"]:
        if not CharacterStore._all_characters:
            await cls.load_all_characters()
        return list(CharacterStore._all_characters.values())

    @classmethod
    async def create_new_character(cls, note) -> "Character":
        c = await new_character(note, 4)
        print(c)
        c = cls(**json.loads(c))
        c.save()
        return c
