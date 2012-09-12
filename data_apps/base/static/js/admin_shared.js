function getId(str_id)
{
	var arr = str_id.split('_');
	return parseInt(arr[arr.length - 1]);
}

/* requires jQueryUI */
function makeSortable(selector, sortable_items, url)
{
	var ajax_indicator = $('.ajax_indicator');
	var sortable_element = $(selector);
	
	sortable_element.sortable({
		'axis' : 'y',
		'opacity' : 0.5,
		'items' : sortable_items,
		'update' : function()
		{
			var pk_ids = new Array;
			$(this).find('li').each(function(e, ui){
				var id = getId($(this).attr('id'));
				if(!isNaN(id)) pk_ids.push(id);
			});
			
			$.ajax({
				type : 'POST',
				url : url,
				data : {'pk_ids' : [jQuery.unique(pk_ids).toString()], 'fk' : getId($(this).attr('id'))},
				beforeSend: function()
				{
					ajax_indicator.show();
				},
				complete: function()
				{
					ajax_indicator.hide();
					sortable_element.effect('highlight');
				}
			});
		}
	});
}

function append_paging_querystring_value(param)
{
	var pattern = "[\\?&]" + param + "=([^&#]*)";
	var regex = new RegExp(pattern);
	var tmp_url = window.location.href;
	var results = regex.exec(tmp_url);
	if (results != null) 
	{
		$.each($('table a, a.append_qs_values'), function(i, element){
			$(element).attr('href', element.href + '?p=' + results[1])
		});
	}
}