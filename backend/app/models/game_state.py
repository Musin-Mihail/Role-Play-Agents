from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class InteractiveObject(BaseModel):
    name: str
    location: str
    state: str


class Scene(BaseModel):
    location: str
    time: str
    description: str
    interactive_objects: List[InteractiveObject] = Field(default_factory=list)


class Relationship(BaseModel):
    target: str
    type: str


class Clothing(BaseModel):
    head: List[str] = Field(default_factory=list)
    face: List[str] = Field(default_factory=list)
    underwear: List[str] = Field(default_factory=list)
    torso: List[str] = Field(default_factory=list)
    body: List[str] = Field(default_factory=list)
    overwear: List[str] = Field(default_factory=list)
    legs: List[str] = Field(default_factory=list)
    feet: List[str] = Field(default_factory=list)
    hands: List[str] = Field(default_factory=list)


class Character(BaseModel):
    age: int
    description: str
    personality: str
    current_action: str
    current_emotion: List[str] = Field(default_factory=list)
    goal: str
    knowledge: List[str] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
    location_in_scene: str
    clothing: Clothing = Field(default_factory=Clothing)
    inventory: List[str] = Field(default_factory=list)
    holding: List[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore")


class GameState(BaseModel):
    """
    Root model representing the entire state.json file.
    """

    scene: Scene
    characters: Dict[str, Character]

    model_config = ConfigDict(extra="ignore")
