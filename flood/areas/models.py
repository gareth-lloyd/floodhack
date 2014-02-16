from django.contrib.gis.db import models


class Area(models.Model):
    fwd_tacode = models.CharField(max_length=255, unique=True)
    fwa_name = models.CharField(max_length=255, null=True, blank=True)
    descrip = models.CharField(max_length=255, null=True, blank=True)
    river_sea = models.CharField(max_length=255, null=True, blank=True)
    gid = models.CharField(max_length=255, null=True, blank=True)
    w_region = models.CharField(max_length=255, null=True, blank=True)
    w_descrip = models.CharField(max_length=255, null=True, blank=True)
    w_fwa_name = models.CharField(max_length=255, null=True, blank=True)
    fwis_code = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    area = models.CharField(max_length=255, null=True, blank=True)
    e_qdial = models.CharField(max_length=255, null=True, blank=True)
    w_afon = models.CharField(max_length=255, null=True, blank=True)
    w_qdial = models.CharField(max_length=255, null=True, blank=True)
    county = models.CharField(max_length=255, null=True, blank=True)

    parent = models.ForeignKey('areas.Area', null=True, blank=True,
                               related_name='parent_area')
    shape = models.PolygonField(blank=True, null=True)

    objects = models.GeoManager()


