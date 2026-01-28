from backend.app.main import app as fastapi_app

# Expose ASGI app explicitly
app = fastapi_app
