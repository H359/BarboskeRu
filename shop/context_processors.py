from models import Category
from basket import Basket

def common_pieces(request):
    categories = Category.get_tree()
    if request.is_ajax():
	template = 'base_ajax.html'
    else:
	template = 'base.html'
    return {
	'base_template': template,
	'shop': {
            'basket': Basket(request),
	    'categories': categories
	}
    }
