from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from filer.fields.file import FilerFileField


class Widget(models.Model):
    file = FilerFileField(null=True)


class Widget2(models.Model):
    content_type = models.ForeignKey(ContentType)
    content_id = models.PositiveIntegerField()
    content = GenericForeignKey('content_type', 'content_id')

    file = FilerFileField()
