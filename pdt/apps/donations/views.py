from django.views.generic import TemplateView


class DonationView(TemplateView):
    template_name = "donations/index.html"
