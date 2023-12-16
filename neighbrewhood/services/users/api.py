from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry

from ninja import Router
from ninja.responses import codes_4xx
from ninja_jwt.authentication import JWTAuth

from common.schemas import DefaultError
from brewers.models import Brewer
from services.common.brewers_api import profile_required
from .schemas import BrewerResponseSchema, CreateBrewerSchema, UserSchema, UserRegisterSchema


users_router = Router(tags=["Users", "Brewers"])
User = get_user_model()

@users_router.get(
    "me", 
    auth=JWTAuth(), 
    response={200: UserSchema, codes_4xx: DefaultError},
    url_name="users_me"
)
def me(request):
    return request.user

@users_router.post(
    "register", 
    response={201: UserSchema, codes_4xx: DefaultError},
    url_name="users_register",
)
def register(request, user_details: UserRegisterSchema):
    try:
        new_user = User.objects.create_user(
            username=user_details.username,
            password=user_details.password,
            email=user_details.email,
            first_name=user_details.first_name,
            last_name=user_details.last_name,
        )
        new_user.is_active = True
        new_user.save()
    except Exception as e:
        return 400, {"detail": str(e)}
    return 201, new_user

@users_router.post(
    "createBrewerProfile", 
    auth=JWTAuth(), 
    response={201: BrewerResponseSchema, codes_4xx: DefaultError},
    url_name="users_create_brewer",
)
def create_brewer(request, brewer: CreateBrewerSchema):
    if getattr(request.user, "brewer", False):
        return 400, {'detail': "You already have a brewer profile."}
    
    try:
        brewer_obj = Brewer.objects.create(
            location=GEOSGeometry(brewer.location_str),
            phone_number=brewer.phone_number,
            user=request.user,
            can_claim=True,
        )
    except Exception as e:
        return 400, {'detail': str(e)}

    return 201, brewer_obj

@users_router.get(
    "profile", 
    auth=JWTAuth(), 
    response={200: BrewerResponseSchema, codes_4xx: DefaultError},
    url_name="users_profile"
)
@profile_required
def brewer_profile(request):
    return request.user.brewer
