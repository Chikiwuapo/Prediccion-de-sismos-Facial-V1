import os

# Ensure Django settings are set before importing the Django ASGI application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logic.settings')

from django.core.asgi import get_asgi_application as get_django_asgi  # noqa: E402
from fastapi_auth.main import app as fastapi_app  # noqa: E402
from starlette.applications import Starlette  # noqa: E402
from starlette.responses import JSONResponse  # noqa: E402
from starlette.routing import Mount, Route  # noqa: E402

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
        # Mount FastAPI authentication under /auth
        Mount('/auth', app=fastapi_app),
        # Mount Django app (your REST API) under /api
        Mount('/api', app=_django_asgi_app),
    ]
)
