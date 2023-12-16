from typing import List
from ninja import ModelSchema

from brewswaps.models import BrewSwap
from services.brewservice.schemas import BrewResponseSchema
from services.users.schemas import UserLimitedSchema


class BrewSwapCreateSchema(ModelSchema):
    brew: int
    max_increment: int = None

    class Meta:
        model = BrewSwap
        fields = [
            "brew",
            "total_bottles",
            "max_increment",
        ]

class BrewSwapResponseSchema(ModelSchema):
    brew: BrewResponseSchema
    bottles_available: int
    creator: UserLimitedSchema

    @staticmethod
    def resolve_bottles_available(obj):
        return obj.bottles_available

    class Meta:
        model = BrewSwap
        fields = [
            "brew",
            "total_bottles",
            "max_increment",
            "creator",
        ]
