"""Build the app: settings, database, routes, error shapes and request IDs."""

from __future__ import annotations

import re
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from . import __version__, bugs, errors
from .api import admin, auth, cart, orders, products, tools, users
from .clock import Clock
from .config import Settings
from .database import prepare, sync_reporting
from .db import make_engine, make_sessionmaker
from .mailer import Outbox
from .reporting import SyncLoop
from .reviews import MongoReviews, SqlReviews
from .security import make_hasher
from .web import errors as web_errors
from .web import routes as web_routes
from .web.helpers import make_templates

SAFE_REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
STATIC = Path(__file__).resolve().parent / "static"
CSP = (
    "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
    "form-action 'self'; frame-ancestors 'none'; base-uri 'none'; object-src 'none'"
)

DESCRIPTION = """
**Bookshelf** is the Practice App for [myOpenSDET](https://arshaduzzaman-sm.github.io/myopensdet/):
a small online shop for books and study gadgets.

> For practice on your own computer only. Never deploy it to the internet.

The shop's web pages are at [/](/). This page lists the API.

**Try it:** `POST /api/auth/login` with `{"username": "arshad", "password": "Test@1234"}`,
copy the `access_token`, press **Authorize** and paste it.

Every error looks like `{"error": {"code": "...", "message": "...", "request_id": "..."}}`.
Every response has an `X-Request-ID` header.
"""


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    bugs.switch(settings.planted_bugs)
    for url in (settings.database_url, settings.reporting_database_url):
        if url.startswith("sqlite:///"):
            Path(url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        loop = SyncLoop(lambda: sync_reporting(app), settings.reporting_sync_seconds)
        loop.start()
        yield
        loop.stop()

    app = FastAPI(
        lifespan=lifespan,
        title="Bookshelf Practice App",
        version=__version__,
        description=DESCRIPTION,
        docs_url="/docs",
        redoc_url=None,
        openapi_url="/openapi.json",
    )
    app.state.settings = settings
    app.state.engine = make_engine(settings.database_url)
    app.state.sessionmaker = make_sessionmaker(app.state.engine)
    app.state.reporting_engine = make_engine(settings.reporting_database_url)
    app.state.reporting_sessionmaker = make_sessionmaker(app.state.reporting_engine)
    if settings.mongodb_url:
        app.state.reviews = MongoReviews(settings.mongodb_url, settings.mongodb_database)
    else:
        app.state.reviews = SqlReviews(app.state.sessionmaker)
    app.state.clock = Clock()
    app.state.outbox = Outbox(
        settings.outbox_dir, settings.smtp_host, settings.smtp_port, settings.mail_from
    )
    app.state.hasher = make_hasher(settings.fast_password_hashing)
    app.state.templates = make_templates()
    prepare(app)

    errors.install(app)
    web_errors.install(app)

    @app.middleware("http")
    async def request_id(request: Request, call_next):
        incoming = request.headers.get("X-Request-ID", "")
        request.state.request_id = incoming if SAFE_REQUEST_ID.match(incoming) else uuid.uuid4().hex
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        if web_errors.is_web(request):
            # Web pages load only this app's own files: no inline or outside scripts.
            response.headers.setdefault("Content-Security-Policy", CSP)
            response.headers.setdefault("X-Frame-Options", "DENY")
            response.headers.setdefault("Referrer-Policy", "same-origin")
        return response

    for module in (auth, users, products, cart, orders, admin, tools):
        app.include_router(module.router, prefix="/api")
    app.include_router(web_routes.router)
    app.mount("/static", StaticFiles(directory=STATIC), name="static")

    return app
