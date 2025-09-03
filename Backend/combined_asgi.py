import os

# Ensure Django settings are set before importing the Django ASGI application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logic.settings')

from django.core.asgi import get_asgi_application as get_django_asgi  # noqa: E402
from fastapi_auth.main import app as fastapi_app  # noqa: E402
from starlette.applications import Starlette  # noqa: E402
from starlette.responses import JSONResponse  # noqa: E402
from starlette.routing import Mount, Route  # noqa: E402
from starlette.middleware.cors import CORSMiddleware  # noqa: E402

# Instantiate Django ASGI app
_django_asgi_app = get_django_asgi()


def healthz(_request):
    return JSONResponse({"status": "ok"})


def root(_request):
    return JSONResponse({
        "service": "Combined ASGI",
        "status": "running",
        "endpoints": {
            "auth": "/auth",
            "api": "/api",
            "health": "/healthz",
        }
    })

# Starlette app that mounts both FastAPI (auth) and Django (api)
app = Starlette(
    routes=[
        Route('/', endpoint=root),
        Route('/healthz', endpoint=healthz),
        Mount('/auth', app=fastapi_app),
        Mount('/api', app=_django_asgi_app),
    ]
)

# Apply CORS globally so both mounts (and any 404) include headers
_origins_env = os.getenv('CORS_ALLOWED_ORIGINS', '')
_origin_regex = os.getenv('CORS_ALLOWED_ORIGIN_REGEX', '')
_allowed_origins = [o.strip() for o in _origins_env.split(',') if o.strip()]

cors_kwargs = {
    'allow_credentials': False,
    'allow_methods': ["*"],
    'allow_headers': ["*"],
    'expose_headers': ["*"],
}

if _origin_regex:
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=_origin_regex,
        **cors_kwargs,
    )
elif _allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_allowed_origins,
        **cors_kwargs,
    )
