from ninja import Router

from .views import importer

importer_router = Router()
importer_router.add_router("importer", importer, tags=["importing"])


__all__ = ["importer_router"]
