var decorateLinks = function() {
    $('a[href^="/"]').each(function(i,link){
	link = $(link);
	link.attr('href', '#!' + link.attr('href'));
    });
}

var linkLoaded = function(data){
    $('#bodyCopy').html(data);
    decorateLinks();
    $('#ajax_loader').hide();
}


var formLoaded = function(data){
    // hide ajax loader
    $('#ajax_loader').hide();
    console.log(data);
}

var loadLink = function(link){
    $('#ajax_loader').show();
    $.get(link, linkLoaded);
}

var loadForm = function(form){
    // show ajax loader
    $.post(form.attr('action'), form.serializeArray(), formLoaded);
}

$(document).ready(function(){
    decorateLinks();
    $(document).on('submit', function(evt){
	loadForm($(evt.target));
	return false;
    });
    $.history.init(function(hash){
	var spl = hash.split("!");
	if (spl.length > 1) loadLink(spl[1]);
    });
});