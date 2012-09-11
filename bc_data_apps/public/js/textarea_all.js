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
    width  : "800",
    remove_script_host : false,
    relative_urls : false,
    paste_auto_cleanup_on_paste : true,
    cleanup_callback : "myCustomCleanup",
    theme_advanced_buttons1 : "bold, italic, underline, separator, undo, redo, separator, cleanup, separator, bullist, numlist, separator,outdent,indent,blockquote,justifyleft, justifycenter, justifyright,",
    theme_advanced_buttons2 : "image, link, unlink, separator, forecolor, separator, formatselect, code,",
    theme_advanced_buttons3_add : "pastetext, pasteword, selectall"
});