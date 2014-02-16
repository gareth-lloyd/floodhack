from django.views.generic import TemplateView

from journo.models import Status


class Map(TemplateView):
    template_name = "journo/map.html"

    def _mentions(self):
        return Status.objects.filter(reply_to_bot=True).order_by('-created_date')[:20]

    def get_context_data(self, **kwargs):
        context = kwargs
        context.update(timeline=self._mentions())
        return context
