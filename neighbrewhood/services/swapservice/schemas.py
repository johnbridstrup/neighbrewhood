from typing import Dict
from django.urls import reverse_lazy
from ninja import ModelSchema

from brewswaps.models import BrewSwap
from common.schemas import ActionUrlSchema, HttpMethod, make_action
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
            "status",
        ]

class BrewSwapResponseSchema(ModelSchema):
    brew: BrewResponseSchema
    bottles_available: int
    creator: UserLimitedSchema
    distance: float = None
    detail: ActionUrlSchema

    @staticmethod
    def resolve_bottles_available(obj):
        return obj.bottles_available
    
    @staticmethod
    def resolve_distance(obj):
        return float(obj.distance.m)
    
    @staticmethod
    def resolve_detail(obj):
        url = reverse_lazy("api-1.0.0:brewswaps_detail", args=[obj.id])
        return make_action(HttpMethod.GET, str(url))

    class Meta:
        model = BrewSwap
        fields = [
            "brew",
            "total_bottles",
            "max_increment",
            "creator",
            "status",
        ]


class BrewSwapDetailResponseSchema(BrewSwapResponseSchema):
    actions: Dict[str, ActionUrlSchema] = None

    @staticmethod
    def resolve_actions(obj, context):
        request = context["request"]
        if request.user == obj.creator:
            setlive_url = reverse_lazy("api-1.0.0:brewswaps_set_live", args=[obj.id])
            setcomplete_url = reverse_lazy("api-1.0.0:brewswaps_set_complete", args=[obj.id])
            return {
                "set_live": make_action(HttpMethod.GET, str(setlive_url)),
                "set_complete": make_action(HttpMethod.GET, str(setcomplete_url)),
            }
        return 