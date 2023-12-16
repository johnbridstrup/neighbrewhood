from ninja import Router
from ninja.responses import codes_4xx
from ninja_jwt.authentication import JWTAuth

from brews.models import Brew
from brewswaps.models import BrewSwap
from common.schemas import DefaultError
from .schemas import BrewSwapCreateSchema, BrewSwapResponseSchema


swap_router = Router(tags=["Brewers", "Brews", "Swaps"])

@swap_router.post(
    "createSwap", 
    auth=JWTAuth(), 
    response={201: BrewSwapResponseSchema, codes_4xx: DefaultError},
    url_name="brewswaps_create_swap",
)
def create_swap(request, swap: BrewSwapCreateSchema):
    try:
        brew = Brew.objects.get(id=swap.brew)
    except Brew.DoesNotExist:
        return 404, {'detail': f'Brew with id {swap.brew} does not exist'}
    
    if not brew.is_brewed_by(request.user):
        return 403, {'detail': f"You cannot create a swap if you aren't the brewer"}
    
    swap_obj = BrewSwap(
        brew=brew,
        total_bottles=swap.total_bottles,
        creator=request.user,
    )

    if swap.max_increment:
        swap_obj.max_increment = swap.max_increment
    
    swap_obj.save()
    return 201, swap_obj
