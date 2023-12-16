from functools import wraps


def profile_required(f):
    @wraps(f)
    def check_for_profile(request, *args, **kwargs):
        def no_profile_resp(request, *args, **kwargs):
            return 404, {"detail": "You must create a profile"}
        try:
            request.user.brewer
        except AttributeError:
            return no_profile_resp(request, *args, **kwargs)
        return f(request, *args, **kwargs)
    return check_for_profile