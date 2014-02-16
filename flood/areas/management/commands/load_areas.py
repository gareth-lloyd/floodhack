import gc
import shapefile
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Polygon, Point


FIELDS =  ['fwd_tacode', 'fwa_name', 'descrip', 'river_sea', 'gid',
'w_region', 'w_descrip', 'w_fwa_name', 'fwis_code', 'region', 'area',
'e_qdial', 'parent', 'w_afon', 'w_qdial', 'county']


OSGB = 27700
WGS = 4326

def _shape(points):
    if points[0] != points[-1]:
        points.append(points[0])
    try:
        poly = Polygon([Point(*p, srid=OSGB) for p in points], srid=OSGB)
        poly.transform(WGS)
        return poly
    except Exception, e:
        print points
        print e
        raise


def _attrs(shape_record, fields):
    from areas.models import Area
    attrs = {fld: shape_record.record[i] for i, fld in enumerate(fields)}
    attrs.update(shape=_shape(shape_record.shape.points))

    if 'parent' in fields:
        fwd_tacode = shape_record.record[0]
        try:
            attrs.update(parent=Area.objects.get(fwd_tacode=fwd_tacode))
        except Area.DoesNotExist:
            attrs.pop('parent')

    return attrs

class Command(BaseCommand):
    args = ''
    help = 'Run the worker process'

    def handle(self, *args, **options):
        from areas.models import Area

#        reader = shapefile.Reader('data/EA_FloodAlertAreas/eadeaew00020008')
#        fields = list(FIELDS)
#        fields.remove('parent')
#
#        recs = reader.shapeRecords()
#        for shape_record in recs:
#            attrs = _attrs(shape_record, fields)
#            fwd_tacode = attrs['fwd_tacode']
#            if Area.objects.filter(fwd_tacode=fwd_tacode).exists():
#                continue
#
#            print Area.objects.create(**_attrs(shape_record, fields))
#            gc.collect()


        reader = shapefile.Reader('data/EA_FloodWarningAreas/flood_warning_areas_010k')
        recs = reader.shapeRecords()
        for shape_record in recs:
            attrs = _attrs(shape_record, FIELDS)
            fwd_tacode = attrs['fwd_tacode']
            if Area.objects.filter(fwd_tacode=fwd_tacode).exists():
                continue

            print Area.objects.create(**attrs)
            gc.collect()
