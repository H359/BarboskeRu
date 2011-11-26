#from django.views.generic import ListView, DetailView
from django.shortcuts import Http404

from annoying.decorators import render_to

from models import Category, Ware
from basket import BasketView

@render_to('shop/category.html')
def category(request, path=None):
    tree = Category.get_tree()
    res = {}
    if path is None:
        res['root'] = tree[0]
    else:
        if path.endswith('.html'):
            ware_slug = path.split('/')[-1][:-5]
            path = path[0:len(path)-len(ware_slug)-6]
            res['ware'] = Ware.objects.get(slug=ware_slug)
            res['TEMPLATE'] = 'shop/ware.html'
        candidates = [x for x in tree if x._materialized_path == path]
        if len(candidates) <> 1:
            raise Http404
        res['root'] = candidates[0]
    return res

basket = BasketView.as_view()
