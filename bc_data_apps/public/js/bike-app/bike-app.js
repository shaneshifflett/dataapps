$(document).ready(function() {
	$("#raw-data-table").tablesorter({widgets: ['zebra'], sortList: [[1,0]]})
    $('.filters .filteroptions input[type=checkbox]').hide();
    $('.filters .filteroptions span.check').show();
    $(".filters span.check").click(function() {
		$(this).toggleClass("checked");
		$(this).next().click();
	});
	
	
	/* This is basic - uses default settings */

	//$("a#single_image").fancybox();

	/* Using custom settings */

    // $("a#report-accident").fancybox({
    //  'hideOnContentClick': true
    // });

	/* Apply fancybox to multiple items */

    // $("a.group").fancybox({
    //  'transitionIn'  :   'elastic',
    //  'transitionOut' :   'elastic',
    //  'speedIn'       :   600, 
    //  'speedOut'      :   200, 
    //  'overlayShow'   :   false
    // });

});        
