var draw = function($, root){
        var w = 960,
            h = 500,
            shapeSize = 8,
            data = [root],
        tree = d3.layout.tree().size([w - 20, h - 50]),
        diagonal = d3.svg.diagonal().projection(function(d){ return [d.x, d.y]; });

    var vis = d3.select('div.ast_root').append('svg:svg')
        .attr('width', w)
        .attr('height', h)
      .append('svg:g')
        .attr('transform', 'translate(20, 20)');

    var nodes = tree.nodes(root);

    var link = vis.selectAll('g.link')
		 .data(tree.links(nodes))
	       .enter().append('svg:g')
	         .attr('class', 'link');

    var link_text = function(d, i) {
	// FIXME: dirty hack
	if (d.source.x < d.target.x) return 'False';
	return 'True';
	/*return i + ' - ' + d.source.name + ' -> ' + d.target.name;*/
    };
    middle = function(x,p){
	var left = d3.min([x.target[p], x.source[p]]),
	    right = d3.max([x.target[p], x.source[p]]);
	return left + 0.5*(right-left);
    }

    link.filter(function(d){ return d.source.lexeme == 'IF'; })
      .append('svg:text')
        .attr('dy', function(d){ return middle(d, 'y'); })
        .attr('dx', function(d){ return middle(d, 'x'); })
        .attr('transform', function(d){ return 'translate(' + ((d.source.x > d.target.x ? -1 : 0.25)*50) + ', 0)'; }) /* TODO: this should depend on text length */
        .text(link_text);
    link.append('svg:path').attr('d', diagonal);

    var node = vis.selectAll('g.node')
		 .data(nodes)
	       .enter().append('svg:g')
	         .attr('class', 'node')
	         .attr('transform', function(d){ return 'translate(' + d.x + ', ' + d.y + ')'; });

    /* IF -> skewed rectangle */
    node.filter(function(d){ return d.lexeme == 'IF'; })
      .append('svg:rect')
        .attr('width', 2*shapeSize)
        .attr('height', 2*shapeSize)
        .attr('transform', function(d){ return 'skewX(-15) translate(-' + shapeSize + ', -' + shapeSize + ')';});
    
    /* RESULT -> terminal circle */
    node.filter(function(d){ return d.lexeme == 'RESULT'; })
      .append('svg:circle')
        .attr('r', 1);
    
    /* entry point -> initial circle */
    node.filter(function(d){ return !d.lexeme && d.depth == 0; })
      .append('svg:circle')
        .attr('r', 1);

    node.append('svg:text')
	.attr('dx', function(d){ return (shapeSize+5)*(d.children ? -1 : 1); })
	.attr('dy', 3)
	.attr('text-anchor', function(d){ return d.children ? 'end' : 'start'; })
	.text(function(d){ return d.name; });

    /*
    vis.selectAll("circle")
        .data(tree(root))
      .enter().append("svg:circle")
        .attr("class", "node")
        .attr("r", 3.5)
        .attr("cx", x)
        .attr("cy", y);

    function update() {
      if (data.length >= 500) return clearInterval(timer);

      // Add a new datum to a random parent.
      var d = {id: data.length}, parent = data[~~(Math.random() * data.length)];
      if (parent.children) parent.children.push(d); else parent.children = [d];
      data.push(d);

      // Compute the new tree layout. We'll stash the old layout in the data.
      var nodes = tree.nodes(root);

      // Update the nodes…
      var node = vis.selectAll("circle.node")
          .data(nodes, function(d) { return d.id; });

      // Enter any new nodes at the parent's previous position.
      node.enter().append("svg:circle")
          .attr("class", "node")
          .attr("r", 3.5)
          .attr("cx", function(d) { return d.parent.x0; })
          .attr("cy", function(d) { return d.parent.y0; })
        .transition()
          .duration(duration)
          .attr("cx", x)
          .attr("cy", y);

      // Transition nodes to their new position.
      node.transition()
          .duration(duration)
          .attr("cx", x)
          .attr("cy", y);

      // Update the links…
      var link = vis.selectAll("path.link")
          .data(tree.links(nodes), function(d) { return d.target.id; });

      // Enter any new links at the parent's previous position.
      link.enter().insert("svg:path", "circle")
          .attr("class", "link")
          .attr("d", function(d) {
            var o = {x: d.source.x0, y: d.source.y0};
            return diagonal({source: o, target: o});
          })
        .transition()
          .duration(duration)
          .attr("d", diagonal);

      // Transition links to their new position.
      link.transition()
          .duration(duration)
          .attr("d", diagonal);
    }

    function x(d) {
      return d.x0 = d.x;
    }

    function y(d) {
      return d.y0 = d.y;
    }
    */
};

var pt_tree = {
    'name': 'Вход',
    'comment': 'Точка входа',
    'children': [
	{'name': 'price > 10', 'lexeme': 'IF',
	 'children': [
	    {'name': 'ware.category == <CATEGORY_STUB>', 'lexeme': 'IF',
	     'children': [
	       {'name': 'return 8', 'lexeme': 'RESULT'},
	       {'name': 'return 1', 'lexeme': 'RESULT'}
	     ]
	    },
	    {'name': '+', 'lexeme': 'OPERATOR',
	     'children': [
	        {'name': '5', 'lexeme': 'CONSTANT'},
	        {'name': 'price', 'lexeme': 'VARIABLE'}
	     ]
	     }
	 ]
	}
    ]
};

django.jQuery(document).ready(function(){ 
    django.jQuery('div.ast_root > div').hide();
    draw(django.jQuery, pt_tree);
});