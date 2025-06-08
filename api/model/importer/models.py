import uuid

from django.db import models


class Importer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4) # type: ignore
    name = models.CharField(max_length=255) # type: ignore
    description = models.TextField() # type: ignore
