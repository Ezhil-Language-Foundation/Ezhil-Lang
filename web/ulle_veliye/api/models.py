# -*- coding: utf-8 -*-

from django.db import models

# Create your models here.


class Snippet(models.Model):
    code = models.TextField()
    output = models.TextField()
    is_success = models.BooleanField(default=True)
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Created At",)
    modified_at = models.DateTimeField(
        auto_now=True, verbose_name="Last Modified At")
