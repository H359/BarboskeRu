var linkLoaded = function(data){
    // hide ajax loader
    $('#ajax_loader').hide();
    $('#bodyCopy').html(data);
}


var formLoaded = function(data){
    // hide ajax loader
    $('#ajax_loader').hide();
    console.log(data);
}

var loadLink = function(link){
    // show ajax loader
    $('#ajax_loader').show();
    window.location.hash = '#!' + link.attr('href');
    $.get(link.attr('href'), linkLoaded);
}

var loadForm = function(form){
    // show ajax loader
    $.post(form.attr('action'), form.serializeArray(), formLoaded);
}

$(document).ready(function(){
    $(document).on('click', 'a[href*="/"]', function(evt){
	var target = $(evt.target);
	if (evt.target.nodeName != 'A') target = target.parents('a');
	loadLink(target);
	return false;
    });
    $(document).on('submit', function(evt){
	loadForm($(evt.target));
	return false;
    });
});