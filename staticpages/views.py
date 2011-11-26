from django.shortcuts import get_object_or_404
from models import StaticPage

from annoying.decorators import render_to

@render_to('staticpages/page.html')
def page(request, url):
    return {'page': get_object_or_404(StaticPage, url=url)}
