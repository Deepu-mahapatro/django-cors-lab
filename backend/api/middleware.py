
from django.http import HttpResponse
from django.utils.cache import patch_vary_headers


ALLOWED_ORIGINS = {
    "http://127.0.0.1:5500",
}

ALLOWED_METHODS = {
    "GET",
    "POST",
    "PATCH",
    "DELETE",
}

ALLOWED_HEADERS = {
    "content-type",
    "authorization",
    "x-csrftoken",
}


class ManualCORSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.headers.get("Origin")

        # 1. Detect a CORS preflight request.
        is_preflight = (
            request.method == "OPTIONS"
            and "Access-Control-Request-Method" in request.headers
        )

        # 2. Handle preflight before normal Django processing.
        if is_preflight:
            requested_method = request.headers.get(
                "Access-Control-Request-Method", ""
            ).upper()

            requested_headers = {
                header.strip().lower()
                for header in request.headers.get(
                    "Access-Control-Request-Headers", ""
                ).split(",")
                if header.strip()
            }

            allowed = (
                origin in ALLOWED_ORIGINS
                and requested_method in ALLOWED_METHODS
                and requested_headers.issubset(ALLOWED_HEADERS)
            )

            # Reject unapproved preflight requests.
            if not allowed:
                return HttpResponse(status=403)

            # Approve the preflight request.
            response = HttpResponse(status=204)

            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Methods"] = ", ".join(
                sorted(ALLOWED_METHODS)
            )
            response["Access-Control-Allow-Headers"] = (
                "Content-Type, Authorization, X-CSRFToken"
            )
            response["Access-Control-Allow-Credentials"] = "true"
            response["Access-Control-Max-Age"] = "600"

            patch_vary_headers(
                response,
                (
                    "Origin",
                    "Access-Control-Request-Method",
                    "Access-Control-Request-Headers",
                ),
            )

            return response

        # 3. Process normal requests through Django.
        response = self.get_response(request)

        # 4. Add CORS headers to responses from allowed origins.
        if origin in ALLOWED_ORIGINS:
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Credentials"] = "true"

            patch_vary_headers(response, ("Origin",))

        return response
