from ninja import Router
from ninja.pagination import paginate
from ninja.responses import codes_4xx
from ninja_jwt.authentication import JWTAuth
from brewswaps.models import (
    ClaimStatusChoices,
    SwapClaim,
)
from common.schemas import DefaultError, DefaultSuccess
from services.common.brewers_api import profile_required
from services.swapservice.schemas import SwapClaimResponseSchema


claims_router = Router(tags=["Brewers", "Claims"])

# TODO: move these into a separate router
@claims_router.get(
    "{claim_id}/accept",
    auth=JWTAuth(),
    response={200: DefaultSuccess, codes_4xx: DefaultError},
    url_name="claims_accept_claim",
)
@profile_required
def accept_claim(request, claim_id):
    try:
        claim = SwapClaim.objects.get(id=claim_id)
    except SwapClaim.DoesNotExist:
        return 404, {"detail": f"Claim {claim_id} does not exist"}
    if request.user != claim.swap.creator:
        return 403, {"detail": "You can't accept a claim for a swap you didn't create"}
    if claim.swap.bottles_available == 0:
        return 400, {"details": "Can't accept, no bottles remaining"}
    if request.user == claim.creator:
        return 403, {"detail": "You can't accept your own claim"}
    if claim.status == ClaimStatusChoices.CANCELED:
        return 400, {"detail": "This claim has already been canceled by the creator"}
    if claim.swap.bottles_available < claim.num_bottles:
        return 400, {"detail": "Not enough bottles available"}

    msg = claim.accept()
    return 200, {"message": msg}

@claims_router.get(
    "{claim_id}/cancel",
    auth=JWTAuth(),
    response={200: DefaultSuccess, codes_4xx: DefaultError},
    url_name="claims_cancel_claim",
)
@profile_required
def cancel_claim(request, claim_id):
    try:
        claim = SwapClaim.objects.get(id=claim_id)
    except SwapClaim.DoesNotExist:
        return 404, {"detail": f"Claim {claim_id} does not exist"}
    if request.user != claim.creator:
        return 403, {"detail": "You can't cancel someone elses claim. Maybe you meant to reject?"}

    msg = claim.cancel()
    return 200, {"message": msg}

@claims_router.get(
    "{claim_id}",
    auth=JWTAuth(),
    response={200: SwapClaimResponseSchema, codes_4xx: DefaultError},
    url_name="claims_claim_detail",
)
@profile_required
def cancel_claim(request, claim_id):
    try:
        claim = SwapClaim.objects.get(id=claim_id)
    except SwapClaim.DoesNotExist:
        return 404, {"detail": f"Claim {claim_id} does not exist"}

    return 200, claim
