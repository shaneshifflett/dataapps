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
    mode : "textareas",
    theme : "advanced",
    plugins : "paste,inlinepopups",
    height : "400",
    width  : "530",
    remove_script_host : false,
    relative_urls : false,
    paste_auto_cleanup_on_paste : true,
    cleanup_callback : "myCustomCleanup",
    theme_advanced_buttons1 : "bold, italic, underline, separator, undo, redo, separator, bullist, numlist, separator,quote,justifyleft, justifycenter, justifyright, separator, image, link, unlink, separator, code,pastetext, pasteword, selectall",
    theme_advanced_buttons2 : false,
    theme_advanced_buttons3 : false,
    setup : function(ed) {
      // Register example button
      ed.addButton('quote', {
         title : 'quote.desc',
         image : '/public/images/tinymce/quote.gif',
         onclick : function() {
            ed.selection.setContent('<div class="quote"><div class="opener">&ldquo;</div>'+ed.selection.getContent({format : 'text'})+'<div class="closer">&rdquo;</div></div>');
         }
      });
   }
});