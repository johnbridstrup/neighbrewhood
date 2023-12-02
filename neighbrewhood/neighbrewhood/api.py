from ninja_jwt.authentication import JWTAuth
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_extra import NinjaExtraAPI


api = NinjaExtraAPI()
api.register_controllers(NinjaJWTDefaultController)

@api.get("/hello")
def hello(request):
    print(request.user.username)
    return "Hello world"

@api.get("/auth_hello", auth=JWTAuth())
def auth_hello(request):
    return "Authorized hello world"
