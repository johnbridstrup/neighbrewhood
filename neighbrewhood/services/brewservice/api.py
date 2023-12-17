from ninja import Router
from ninja.responses import codes_4xx
from ninja.pagination import paginate
from ninja_jwt.authentication import JWTAuth
from typing import List

from brews.models import Brew, BrewType, Quality
from common.schemas import DefaultError
from services.common.brewers_api import profile_required
from .schemas import BrewCreateSchema, BrewResponseSchema, BrewTypeSchema, QualitySchema


brew_router = Router(tags=["Brewers", "Brews"])

@brew_router.get(
    "brewtypes", 
    auth=JWTAuth(), 
    response=List[BrewTypeSchema],
    url_name="brew_brew_types",
)
@paginate
def brew_types(request):
    return BrewType.objects.all()

@brew_router.get(
    "qualities", 
    auth=JWTAuth(), 
    response=List[QualitySchema],
    url_name="brew_qualities",
)
@paginate
def qualities(request):
    return Quality.objects.all()

@brew_router.get(
    "", 
    auth=JWTAuth(), 
    response=List[BrewResponseSchema],
    url_name="brew_brews",
)
@paginate
def brews(request):
    return Brew.objects.all()

@brew_router.get(
    "myBrews", 
    auth=JWTAuth(), 
    response=List[BrewResponseSchema],
    url_name="brew_my_brews",
)
@profile_required
@paginate
def my_brews(request):
    return request.user.brew_creator.all()

@brew_router.get(
    "brews/{id}", 
    auth=JWTAuth(), 
    response={200: BrewResponseSchema, codes_4xx: DefaultError},
    url_name="brew_brew_detail",
)
def brew(request, id_):
    try:
        return Brew.objects.get(id=id_)
    except Brew.DoesNotExist:
        return 404, {'detail': f'Brew with id {id_} does not exist'}

@brew_router.post(
    "createBrew", 
    auth=JWTAuth(), 
    response={201: BrewResponseSchema, codes_4xx: DefaultError},
    url_name="brew_create_brew",
)
@profile_required
def create_brew(request, brew: BrewCreateSchema):
    brew_type = BrewType.objects.get(id=brew.brew_type)
    qualities = Quality.objects.filter(id__in=brew.qualities)
    brew = Brew.objects.create(
        brew_type=brew_type,
        start_date=brew.start_date,
        completion_date=brew.completion_date,
        notes=brew.notes,
        creator=request.user,
    )
    brew.qualities.set(qualities)
    brew.save()
    return 201, brew
