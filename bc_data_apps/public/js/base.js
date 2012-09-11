/*** Cookie Functions ***/
function setCookie(name,value,days) {
    var expires;
    if (days) {
        var date = new Date();
        date.setTime(date.getTime()+(days*24*60*60*1000));
        expires = "; expires="+date.toGMTString();
    }
    else expires = "";
    document.cookie = name+"="+value+expires+"; path=/";
}

function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}

function deleteCookie(name) {
    setCookie(name,"",-1);
}

/*** Donation Lightbox Popup **/

    /*** Cookie Functions ***/
	function close_donation_lightbox(){
        //setCookie('2011_yearend_donation_lightbox.a','hide',3);
        setCookie('2011_lastchance_donation_lightbox.a','hide',3);
        parent.$.fancybox.close();
	}

function setLBClosed() {
    setCookie('lb-nl-donate','1',3);
}

var citizen = {};
var citizencache = {};

var addthis_config = {
    services_exclude: 'print,email,facebook,twitter',
    ui_delay: 400,
    username: "thebaycitizen"
};

citizen.comments = function() {
    return {
        showReplyForm: function(comment_id, url, person_name) {
            function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie !== '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) == (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            $('#c'+comment_id).parent().hide();
            if($('#replydiv'+comment_id).html()) {
                $('#replydiv'+comment_id).slideDown();
                $('#newComment' + comment_id).focus();
                return;
            }
            var comment_reply = $('#comment' + comment_id);
            var to_add = $( new Array(
                '<div class="newComment" id="replydiv' + comment_id + '" style="padding-left: 3em">',
                '<span class="commenterror" id="replyerror' + comment_id + '"></span>',
                '<form method="POST" action="' + url + '" id="replyform' + comment_id + '">',
                '<input type="hidden" value="' + getCookie('csrftoken') + '" name="csrfmiddlewaretoken">',
                '<textarea name="comment" id="newComment' + comment_id + '"></textarea>',
                '<p><input type="checkbox" name="wants_notifications" checked="checked" /> Receive an email notification if someone replies to your comment.</p>',
                '<input type="image" src="/public/images/layout/button-addComment.png" id="commentsubmit' + comment_id + '" class="submit"><img src="http://media.baycitizen.org/images/icons/ajax-loader.gif" id="commentsubmitloading' + comment_id + '" style="display: none; padding-bottom: 5px; padding-left: 5px;">',
                '</form></div>'
            ).join(''));

            comment_reply.append(to_add);
            to_add.slideDown();
            $('#newComment' + comment_id).focus();
            this.bindForm(comment_id);
        },

        hideReplyForm: function(comment_id) {
            $('#replydiv' + comment_id).slideUp();
            $('#newComment'+comment_id).val('');
            $('#c'+comment_id).parent().show();
        },

        showComments: function(content_id) {
            $.ajax({
                url: '/content/comments/' + content_id + '/',
                success: function(responseText, statusText) {
                   var html = $(responseText);
                   citizencache['comments'+content_id] = true;
                   $('#content_comments').html(html);
                   //$('#comment_status_loading').toggle();
                   $('#content_comments').fadeIn();
                   $('#maincommentform').fadeIn();
                },
                error: function() {alert('Technical difficulties'); $('#comment_status_loading').toggle();}
            });
        },

        bindInitialForm: function() {
            $('#new_comment_form').ajaxForm({
                success: citizen.comments.commentResponse,
                error: citizen.comments.commentError,
                beforeSend: function(){ $('#commenterror').html(''); $('#commentsubmit').attr("disabled", "disabled"); $('#commentsubmitloading').toggle();}
            });
        },

        bindSubmitForm: function(content_id) {
            $('#comment-form').ajaxSubmit({
                success: citizen.comments.commentResponse,
                error: citizen.comments.commentError,
                beforeSend: function(){
                    $('#commenterror').html('');
                    $('#commentsubmit').attr("disabled", "disabled");
                    $('#commentsubmitloading').toggle();
                    if ($("#content_comments:visible").is(":empty")) {
                        citizen.comments.showComments(content_id);
                    }
                }
            });
        },

        bindCommentsOff: function(content_id) {
           $('.comments_count').click(function(e) {
               if(citizencache['comments'+content_id]) {
                   $('#content_comments').fadeIn();
                   $('#commentform').fadeIn();
                   return;
                   }
               //$('#comment_status_loading').toggle();

               citizen.comments.showComments(content_id);
           });
        },

        bindForm: function(comment_id) {
            $('#replyform' + comment_id).ajaxForm({
                success: citizen.comments.commentResponse,
                error: citizen.comments.commentError,
                beforeSend: function(){ $('#replyerror' + comment_id).html(''); $('#commentsubmit' + comment_id).attr("disabled", "disabled"); $('#commentsubmitloading'+comment_id).toggle();}
            });
        },

        commentError: function(request, text, error) {
            if(request.status && request.status > 0) {
                var data = JSON.parse(request.responseText);
                var error_element;
                if(!data.parent_id) {
                    error_element = $('#commenterror');
                    $('#commentsubmit').removeAttr("disabled");
                } else {
                    error_element = $('#replyerror' + data.parent_id);
                    $('#commentsubmit' + data.parent_id).removeAttr("disabled");
                }
                error_element.html(data.errors.join('<br />'));
            } else {
                alert('Unknown error submitting your comment');
            }
        },

        commentResponse: function(responseText, statusText)  {
            var data = JSON.parse(responseText);
            var html = $(data.html);
            html.css("display", "none");
            if(!data.parent_id) {
                $('#newComment').val('');
                $('#content_comments').append(html);
                $('#commentsubmit').removeAttr("disabled");
                $('#commentsubmitloading').toggle();
                $('.dividerBasic').show();
            } else {
                citizen.comments.hideReplyForm(data.parent_id);
                $('#comment' + data.parent_id).after(html);
                $('#commentsubmit' + data.parent_id).removeAttr("disabled");
                $('#commentsubmitloading'+data.parent_id).toggle();
            }
            html.fadeIn();
            $(document).trigger('comment_added');
        },

        inactivate: function(comment_id) {
            $.ajax({
                url: '/comments/comment/' + comment_id + '/inactivate/',
                success: function(responseText, statusText) {
                    $('#comment' + comment_id).fadeOut();
                    var data = JSON.parse(responseText);
                    for(var commentid in data.to_hide) {
                        if (commentid) {
                            $('#comment' + data.to_hide[commentid]).fadeOut();
                            $(document).trigger('comment_removed');
                        }
                    }
                },
                error: function() {alert('Technical difficulties');}
            });
        }
    };
}();

citizen.pagination = function() {
    return {
        errorHandling: function(response, status, xhr) {
            if (status == "error") {
                var msg = "Sorry but there was an error: ";
                $("#pagination-error").html(msg + xhr.status + " " + xhr.statusText);
            }
        }
    };
}();

citizen.dontgo_modal = function() {
    return {
        donate_page: false,
        
        onLoad: function(){
            var donate_re = new RegExp( '^\/(donate|donate2)\/' )
            var path_name = window.location.pathname;
            if( path_name.match(donate_re) ){
                donate_re = new RegExp( '^\/(donate|donate2)\/confirm' )
                if( !path_name.match( donate_re ) ){
                    this.donate_page = true;
                }
            }else{
                if($.cookie('almost_donated')){
                    dontgo_exception = new RegExp('^\/(member-discounts|about\/(employer-matching|donation-faq))');
                    if(path_name.match(dontgo_exception)){
                        this.donate_page = true;
                    }else{
                        $.cookie('almost_donated', null, {path: '/'});
                        $('#almost_donated').fancybox(
                            {   'href': '/donate/dontgo/', 
                                'fixedPosition': true,
                                'onStart':  function(){
                                    $('#fancybox-wrap').css({'top': '8px', 'left': 'auto', 'right': '0px'});
                                }
                            });
                        $('#almost_donated').trigger('click');
                    }
                }
            }
        },

        onUnload: function(){
            if( this.donate_page ) {
                $.cookie('almost_donated', 'true', {expires: .00024, path: '/'});
            }
        }
    };
}();

/*** Django Cross Site Request Forgery protection ***/ 
// https://docs.djangoproject.com/en/dev/ref/contrib/csrf/
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

/*** Main document.onready() event container ***/
// most (if not all) js initializer calls should be added here
$(function() {

    $("a#hidden_link_2011").fancybox({
        'transitionIn'  :   'fade',
        'transitionOut' :   'fade',
        'type'			: 	'iframe',
        'speedIn'       :   600,
        'speedOut'      :   200,
        'overlayShow'   :   true,
        'overlayColor'  :  '#333',
        'width'         :   800,
        'height'        :   510,
        'margin'        :   0,
        'padding'       :   0,
        'scrolling'     :   'no',
        'showCloseButton'   : false,
        'autoScale'     : false,
        'centerOnScroll'    :true,
        'onClosed'		: function() {
        	close_donation_lightbox();
        }
    });

    show_2011_yearend_donation_lightbox = function(){
    if (getCookie('baycitizen.org_donated') !='1' && getCookie('2011_lastchance_donation_lightbox.a') != 'hide' && !((navigator.userAgent.match(/iPhone/i)) || (navigator.userAgent.match(/iPod/i))) && show_2011_donation_lightbox){
            $('a#hidden_link_2011').click();
        } 
    }
    //show_2011_yearend_donation_lightbox();
    $("a.fancy_image").fancybox({
        'titlePosition'  : 'inside'
    });

    $("area.fancy_image").fancybox({
        'titlePosition'  : 'inside'
    });
    
    $('#hot-tabs').tabs();

    $('.socialBar .iComment').click(function() {
        $('#maincommentform').fadeIn();
    });

    $(document).bind('comment_added', function(e) {
        $('.comments_count').each(function(i, o) {
            var p = $(this).html().split(' ');
            var num = parseInt(p[0], 10);
            if(num) {
                num = num + 1;
            } else {
                num = 1;
            }
            var cs = (num > 1) ? "Comments" : "Comment";
            $(this).html(num + " " + cs);
        });
    });

    $(document).bind('comment_removed', function(e) {
        $('.comments_count').each(function(i, o) {
            var p = $(this).html().split(' ');
            var num = parseInt(p[0], 10) - 1;
            var cs = (num > 1) ? "Comments" : "Comment";
            $(this).html(num + " " + cs);
        });
    });

    /*** Meerkat Start ***/
    var scrolled = false;
    $(window).bind('scroll',function(){
        if ( scrolled === false ) {
            // display popup
            if((!('ontouchstart' in window)) && $(window).scrollTop() > 300){
                 $('.meerkat').meerkat({
                    height: '46px',
                    width: '100%',
                    position: 'bottom',
                    close: '.close-meerkat',
                    dontShowAgain: '.close-meerkat',
                    animationIn: 'slide',
                    animationSpeed: 500,
                    cookieExpires: 7
                });
                scrolled = true;
                if ($('#id_email_bottom').length > 0){
                    $('#id_email_bottom').defaultvalue("Email Address");
                }
            }
        }
    });
     /*** Meerkat End ***/

    /*** Set default values for email signup ***/
    if ($('#id_email_end').length > 0 ){
        $('#id_email_end').defaultvalue("Email");
    }
    if ($('#id_email_right').length > 0 ){
        $('#id_email_right').defaultvalue("Email");
    }
    $("#bottomSignupFormSubmit").click( function() {
        $("#newsletterSignupForm-bottom").submit();
    });
    $("#rightSignupFormSubmit").click( function() {
        $("#newsletterSignupForm-right").submit();
    });
    
    /*** dont leave Donate popup ***/
    citizen.dontgo_modal.onLoad();
    
    /*** Fix YouTube videos z-index ***/
    $('iframe[src*="youtube.com"]').each(function() {
		var url = $(this).attr("src");
		$(this).attr("src",url+"&wmode=transparent");
	});
	
});
$(window).unload( function () { 
    citizen.dontgo_modal.onUnload();
});
