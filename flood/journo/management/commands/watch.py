import time
from django.core.management.base import BaseCommand
from journo import gather


class Command(BaseCommand):
    args = ''
    help = 'Run the worker process'

    def handle(self, *args, **options):
        count = 0
        while True:
            try:
                gather.get_datasift_latest(gather._from_id())
                if count % 50 == 0:
                    gather.get_latest_mentions()
            except Exception, e:
                print e

            time.sleep(10)
            count += 1
