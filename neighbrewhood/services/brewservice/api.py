from ninja import Router
from ninja.responses import codes_4xx
from ninja.pagination import paginate
from ninja_jwt.authentication import JWTAuth
from typing import List

from brews.models import Brew, BrewType, Quality
from common.schemas import DefaultError
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
    "brews", 
    auth=JWTAuth(), 
    response=List[BrewResponseSchema],
    url_name="brew_brews",
)
@paginate
def brews(request):
    return Brew.objects.all()

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
    response=BrewResponseSchema,
    url_name="brew_create_brew",
)
def create_brew(request, brew: BrewCreateSchema):
    if not getattr(request.user, "brewer", True):
        return 400, {'detail': "You have not created a profile"}
    
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
    return brew
