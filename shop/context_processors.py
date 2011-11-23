from models import Category

def common_pieces(request):
    categories = Category.get_tree()
    return {
	'shop': {
	    'categories': categories
	}
    }
