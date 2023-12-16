from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.db.models import Q
from ninja import Router
from ninja.pagination import paginate
from ninja.responses import codes_4xx
from ninja_jwt.authentication import JWTAuth
from typing import List

from brews.models import Brew
from brewswaps.models import BrewSwap
from common.schemas import DefaultError
from services.common.brewers_api import profile_required
from .schemas import BrewSwapCreateSchema, BrewSwapResponseSchema


swap_router = Router(tags=["Brewers", "Brews", "Swaps"])

@swap_router.post(
    "createSwap", 
    auth=JWTAuth(), 
    response={201: BrewSwapResponseSchema, codes_4xx: DefaultError},
    url_name="brewswaps_create_swap",
)
@profile_required
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

@swap_router.get(
    "swaps",
    auth=JWTAuth(),
    response={200: List[BrewSwapResponseSchema], codes_4xx: DefaultError},
    url_name="brewswaps_swaps",
)
@profile_required
def swaps(request):
    return 200, BrewSwap.objects.all()

@swap_router.get(
    "mySwaps",
    auth=JWTAuth(),
    response={200: List[BrewSwapResponseSchema], codes_4xx: DefaultError},
    url_name="brewswaps_my_swaps",
)
@profile_required
def my_swaps(request):
    return 200, BrewSwap.objects.filter(creator=request.user).select_related("brew")

@swap_router.get(
    "nearbySwaps",
    auth=JWTAuth(),
    response={200: List[BrewSwapResponseSchema], codes_4xx: DefaultError},
    url_name="brewswaps_nearby_swaps",
)
@profile_required
def nearby_swaps(request, location: str = None, within: int = None):
    if location:
        try:
            location = GEOSGeometry(location)
        except:
            return 400, {'detail': f'Location {location} improperly formatted. Use SRID'}
    else:
        location = request.user.brewer.location
    
    if not within:
        within = 20 # Default to within 20 miles

    query = BrewSwap.objects.filter(~Q(creator=request.user))
    query = query.filter(creator__brewer__location__distance_lte=(location, D(mi=within)))
    query = query.annotate(distance=Distance("creator__brewer__location", location)).order_by("distance")
    query = query.select_related("brew")
    return 200, query
