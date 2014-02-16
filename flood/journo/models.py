from django.contrib.gis.db import models


class Status(models.Model):
    ds_id = models.CharField(max_length=128, unique=True, null=True, blank=True)
    tweet_id = models.CharField(max_length=128, unique=True)

    uid = models.CharField(max_length=128)
    # e.g. @godawful
    username = models.CharField(max_length=128)
    # e.g. Gareth Lloyd
    name = models.CharField(max_length=128)
    avatar = models.URLField(max_length=512, blank=True, null=True)

    created_date = models.DateTimeField()
    content = models.TextField()

    reply_to_bot = models.BooleanField(default=False)
    location = models.PointField(blank=True, null=True)

    objects = models.GeoManager()

class Image(models.Model):
    status = models.ForeignKey(Status)

    url = models.URLField(max_length=512, blank=True, null=True)
