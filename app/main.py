from fastapi import FastAPI
from app.database import engine, Base
from app.models import user, task
from app.routers import auth
Base.metadata.create_all(bind=engine)
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer

app = FastAPI(
    title="Company Task Manager",
    description="Task Management Backend with JWT Auth",
    version="0.1.0"
)


@app.get("/")
def root():
    return {"status": "Backend running 🚀"}

app.include_router(auth.router)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", []).append({"BearerAuth": []})

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
from app.routers import auth, tasks

app.include_router(auth.router)
app.include_router(tasks.router)
