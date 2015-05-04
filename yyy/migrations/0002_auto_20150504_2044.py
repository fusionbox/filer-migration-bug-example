# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filer.fields.file


class Migration(migrations.Migration):

    dependencies = [
        ('yyy', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='widget',
            name='file',
            field=filer.fields.file.FilerFileField(to='filer.File', null=True),
        ),
    ]
