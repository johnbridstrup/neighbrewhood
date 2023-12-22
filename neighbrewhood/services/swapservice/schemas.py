from typing import Dict
from django.urls import reverse_lazy
from ninja import ModelSchema

from brewswaps.models import BrewSwap, SwapClaim
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
    claims: int

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
    
    @staticmethod
    def resolve_claims(obj):
        claims = getattr(obj, "claims", None)
        if claims is not None:
            return claims.count()
        return 0

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
            setinactive_url = reverse_lazy("api-1.0.0:brewswaps_set_inactive", args=[obj.id])
            ret = {
                "set_live": make_action(HttpMethod.GET, str(setlive_url)),
                "set_complete": make_action(HttpMethod.GET, str(setcomplete_url)),
                "set_inactive": make_action(HttpMethod.GET, str(setinactive_url)),
            }
        else:
            make_claim_url = reverse_lazy("api-1.0.0:brewswaps_claim", args=[obj.id])
            ret = {
                "make_claim": make_action(HttpMethod.POST, str(make_claim_url), SwapClaimCreateSchema.json_schema())
            }
        claims_url = reverse_lazy("api-1.0.0:brewswaps_claims", args=[obj.id])
        ret["get_claims"] = make_action(HttpMethod.GET, str(claims_url))
        return ret
    

## Claims
    
class SwapClaimCreateSchema(ModelSchema):
    brew: int

    class Meta:
        model = SwapClaim
        fields = [
            "brew",
            "num_bottles",
        ]

    
class SwapClaimResponseSchema(ModelSchema):
    brew: BrewResponseSchema
    swap: BrewSwapResponseSchema
    creator: UserLimitedSchema
    actions: Dict[str, ActionUrlSchema] = None

    @staticmethod
    def resolve_actions(obj, context):
        request = context["request"]
        if request.user != obj.creator:
            accept_url = reverse_lazy("api-1.0.0:brewswaps_accept_claim", args=[obj.swap.id, obj.id])
            return {
                "accept": make_action(HttpMethod.GET, str(accept_url))
            }
        else:
            cancel_url = reverse_lazy("api-1.0.0:brewswaps_cancel_claim", args=[obj.swap.id, obj.id])
            return {
                "cancel": make_action(HttpMethod.GET, str(cancel_url))
            }
        return {}

    class Meta:
        model = SwapClaim
        fields = [
            "brew",
            "swap",
            "num_bottles",
            "status",
            "creator"
        ]
