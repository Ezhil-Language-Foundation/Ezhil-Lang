# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Snippet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.TextField()),
                ('output', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name=b'Created At')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name=b'Last Modified At')),
            ],
        ),
    ]
