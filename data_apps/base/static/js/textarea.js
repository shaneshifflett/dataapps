function myCustomCleanup(type, value) {
    switch (type) {
        case "get_from_editor":
            return value.replace("\n", "").replace("\r", "");
            
            // Do custom cleanup code here
            break;
        case "insert_to_editor":
            return value.replace("\n", "").replace("\r", "");
            // Do custom cleanup code here
            break;
    }
    return value;
}




tinyMCE.init({
    // General options
    mode : "specific_textareas",
    editor_selector : "largeTE",
    theme : "advanced",
    plugins : "annotate,baycitizenimg,advimage,paste,inlinepopups, table",
    height : "300",
    width  : "550",
    remove_script_host : false,
    relative_urls : false,
    paste_auto_cleanup_on_paste : true,
    cleanup_callback : "myCustomCleanup",
    paste_text_use_dialog: true,
    
    // Theme options
    theme_advanced_statusbar_location : 'top',
    theme_advanced_resizing : true,
    theme_advanced_buttons1 : "bold, italic, underline, separator, undo, redo, separator, cleanup, separator, bullist, numlist, separator,outdent,indent,blockquote,justifyleft, justifycenter, justifyright",
    theme_advanced_buttons2 : "image, link, unlink, separator, fontselect, fontsizeselect, forecolor, separator, formatselect, table, code,",
    theme_advanced_buttons3_add : "annotate,separator,pastetext, pasteword, selectall,separator,related,pagebreaker,baynyt",

    setup : function(ed) {
        // Register example button
        ed.addButton('quote', {
            title : 'quote.desc',
            image : '/public/images/tinymce/quote.gif',
            onclick : function() {
                ed.selection.setContent('<div class="quote"><div class="opener">&ldquo;</div>'+ed.selection.getContent({format : 'text'})+'<div class="closer">&rdquo;</div></div>');
            }
        });
        ed.addButton('related', {
            title : 'Related Module',
            image : '/public/images/tinymce/related.gif',
            onclick : function() {
            	ed.focus();
                ed.selection.setContent('%related%');
            }
        });
        ed.addButton('baynyt', {
            title : 'Appears in the Bay area edition of the NYT',
            image : '/public/images/tinymce/banyt.gif',
            onclick : function() {
            	ed.focus();
                ed.selection.setContent(' <em>This article also appears in the Bay Area edition of The New York Times. </em>');
            }
        });
        ed.addButton('pagebreaker', {
            title : 'Pagination Breakpoint',
            image : '/public/images/tinymce/pagebreaker.png',
            onclick : function() {
                tinyMCE.activeEditor.execCommand('mceInsertContent', false, '<div class="pagebreak">&nbsp;</div>');
            }
        });
    },
    // Example content CSS (should be your site CSS)
    //content_css : "css/example.css",

    // Drop lists for link/image/media/template dialogs
    //template_external_list_url : "js/template_list.js",
    //external_link_list_url : "js/link_list.js",
    //external_image_list_url : "js/image_list.js",
    //media_external_list_url : "js/media_list.js",

    // Replace values for the template plugin
    template_replace_values : {
        username : "Some User",
        staffid : "991234"
    }
});

tinyMCE.init({
    // General options
    mode : "specific_textareas",
    editor_selector : "smallTE",
    theme : "advanced",
    plugins : "annotate,baycitizenimg,advimage,paste,inlinepopups",
    height : "100",
    width  : "550",
    remove_script_host : false,
    relative_urls : false,
    paste_auto_cleanup_on_paste : true,
    cleanup_callback : "myCustomCleanup",
    
    // Theme options
    theme_advanced_buttons1 : "bold, italic, underline, separator, undo, redo, separator, cleanup, separator, bullist, numlist, separator,outdent,indent,blockquote,justifyleft, justifycenter, justifyright,",
    theme_advanced_buttons2 : "image, link, unlink, separator, fontselect, fontsizeselect, forecolor, separator, formatselect, code,",
    theme_advanced_buttons3_add : "annotate,separator,pastetext, pasteword, selectall",

    // Example content CSS (should be your site CSS)
    //content_css : "css/example.css",

    // Drop lists for link/image/media/template dialogs
    //template_external_list_url : "js/template_list.js",
    //external_link_list_url : "js/link_list.js",
    //external_image_list_url : "js/image_list.js",
    //media_external_list_url : "js/media_list.js",

    // Replace values for the template plugin
    template_replace_values : {
        username : "Some User",
        staffid : "991234"
    }
});
