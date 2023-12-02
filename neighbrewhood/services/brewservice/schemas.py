from typing import List
from ninja import ModelSchema

from brews.models import Brew, BrewType, Quality
from services.users.schemas import UserLimitedSchema


class BrewTypeSchema(ModelSchema):
    class Meta:
        model = BrewType
        fields = [
            "value",
            "id",
        ]


class QualitySchema(ModelSchema):
    class Meta:
        model = Quality
        fields = [
            "value",
            "id",
        ]


class BrewCreateSchema(ModelSchema):
    brew_type: int
    qualities: List[int]
    
    class Meta:
        model = Brew
        fields = [
            "brew_type",
            "qualities",
            "start_date",
            "completion_date",
            "notes",
        ]


class BrewResponseSchema(ModelSchema):
    qualities: List[QualitySchema]
    brew_type: BrewTypeSchema
    creator: UserLimitedSchema

    class Meta:
        model = Brew
        fields = [
            "start_date",
            "completion_date",
            "notes",
        ]
