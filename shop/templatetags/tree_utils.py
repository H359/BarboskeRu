from django import template
from django.utils.safestring import mark_safe

register = template.Library()

class RecurseTreeNode(template.Node):
    def __init__(self, template_nodes, queryset_var):
        self.template_nodes = template_nodes
        self.queryset_var = queryset_var
        self.nodelist = []

    def _render_node(self, context, node):
        bits = []
        context.push()
        for child in self.get_children(node):
            context['node'] = child
            bits.append(self._render_node(context, child))
        context['node'] = node
        context['children'] = mark_safe(u''.join(bits))
        rendered = self.template_nodes.render(context)
        context.pop()
        return rendered

    def get_children(self, node):
	return [n for n in self.nodelist if n.parent_id == node.id]

    def render(self, context):
        queryset = self.queryset_var.resolve(context)
    	self.nodelist = queryset
        bits = self._render_node(context, self.nodelist[0])
        return ''.join(bits)

@register.tag
def recursetree(parser, token):
    bits = token.contents.split()
    if len(bits) != 2:
        raise template.TemplateSyntaxError(_('%s tag requires a queryset') % bits[0])

    queryset_var = template.Variable(bits[1])

    template_nodes = parser.parse(('endrecursetree',))
    parser.delete_first_token()

    return RecurseTreeNode(template_nodes, queryset_var)
