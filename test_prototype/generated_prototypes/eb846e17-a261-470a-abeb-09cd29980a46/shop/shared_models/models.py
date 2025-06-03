import uuid

from django.db import models


class Project(models.Model):
    project_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    description = models.TextField()


class System(models.Model):
    system_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()


class Release(models.Model):
    release_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    system = models.ForeignKey(System, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    diagrams = models.JSONField()
    metadata = models.JSONField()
    interfaces = models.JSONField()
    release_notes = models.JSONField()


class Classifier(models.Model):
    classifier_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    system = models.ForeignKey(
        System, on_delete=models.CASCADE, related_name="classifiers"
    )
    data = models.JSONField()


class Interface(models.Model):
    interface_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    system = models.ForeignKey(System, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    actor = models.ForeignKey(Classifier, on_delete=models.CASCADE, null=True)
    data = models.JSONField(default=dict)


class Relation(models.Model):
    relation_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    data = models.JSONField()
    system = models.ForeignKey(
        System, on_delete=models.CASCADE, related_name="relations"
    )
    source = models.ForeignKey(
        Classifier, related_name="relations_to", on_delete=models.CASCADE
    )
    target = models.ForeignKey(
        Classifier, related_name="relations_from", on_delete=models.CASCADE
    )
