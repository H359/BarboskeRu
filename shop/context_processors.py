from models import Category
from basket import Basket

def common_pieces(request):
    categories = Category.get_tree()
    return {
	'shop': {
            'basket': Basket(request),
	    'categories': categories
	}
    }
