from django.shortcuts import render
from django.views.generic import View


# Create your views here.

class HomeView(View):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'index.html')
