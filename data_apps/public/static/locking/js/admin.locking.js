/*
FUTURE REFACTOR: 1.2 makes it easy to make fields read-only with 
the readonly_fields attribute on ModelAdmin. When 1.2 adoption is
more wide-spread, we could make a lot of this javascript superfluous
*/

var app = $.url.segment(1)
var model = $.url.segment(2)
var id = $.url.segment(3)    
var base_url = locking.base_url + "/" + [app, model, id].join("/")

function warning () {
    var minutes = parseInt(locking.timeout/60);
    alert("Your lock on this content will expire in a bit less than five minutes. Please save your content and navigate back to this page to edit the content again for another " + minutes + " minutes.");
}

function locking_mechanism () {
    // locking is pointless when the user is adding a new piece of content
    if (id == 'add') return
    // we disable all input fields pre-emptively, and subsequently check if the content
    // is or is not available for editing
    $(":input").attr("disabled", "disabled")
    $.getJSON(base_url + "/is_locked/", function(lock, status) {
        if (lock.applies && status != '404') {
            var notice = interpolate(gettext('<p class="is_locked">This content is currently being edited by <em>%(for_user)s</em>. You can read it but not edit it.</p>'), lock, true)
            $("#content-main").prepend(notice)
        } else {
            $(":input").removeAttr("disabled")
            $.get(base_url + "/lock/")
            setTimeout(function() {warning()}, (1000*(locking.timeout-300))); 
            $(window).unload(function(){
                // We have to assure that our unlock request actually gets
                // through before the user leaves the page, so it shouldn't
                // run asynchronously.
                $.ajax({'url': base_url + "/unlock/", 'async': false})
            })
        }
    })
}

$(document).ready(function(){
    if ($("body").hasClass("change-form")) {
            locking_mechanism()
    }
})