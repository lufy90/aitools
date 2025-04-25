from django.db import models
from django.contrib.auth.models import User

class BaseModel(models.Model):
    name = models.CharField(max_length=4096)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_created', editable=False)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Annotation(BaseModel):
    pass


class ActionTypes(models.TextChoices):
    pass


class Action(BaseModel):
    is_need_bbox = models.BooleanField(default=True)
    is_need_attr = models.BooleanField(default=True)


class Step(BaseModel):
    annotation = models.ForeignKey(Annotation, related_name='steps', on_delete=models.CASCADE)

    number = models.PositiveIntegerField()
    image = models.ImageField(upload_to='step_images/')
    action = models.ForeignKey(Action, related_name='actions', on_delete=models.CASCADE)
    thinking = models.CharField(max_length=4096, blank=True, null=True)
    bbox_start = models.JSONField(default=list, blank=True, null=True)
    bbox_end = models.JSONField(default=list, blank=True, null=True)
    action_attr = models.CharField(max_length=1024, blank=True, null=True)

    def __str__(self):
        return f"Step {self.number} of {self.annotation.name}"

    class Meta:
        ordering = ['number']
