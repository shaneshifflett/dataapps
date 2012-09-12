$(document).ready(function() {
    $('input[name=amounts]').click(function() {
       $('input[name=other]:checked').attr('checked', false);
       $('.other_amount').val('');
    });
    
    $("input[type=radio]:checked + label").addClass("greenLabel");
    
    $("input[type=radio]").change(function() {
    	$(this).parent().find("label.greenLabel").removeClass("greenLabel");
    	var id = $(this).attr("id");
    	$("label[for="+id+"]").addClass("greenLabel");
    });

    /* this is the gift choice disabling code
     * it relys on some json like data generated in the template.
     * */
    $('form').submit(function(e){
        if ( window.gift_error_state){
            e.stopPropagation();
            e.preventDefault(); 
            window.location.hash = '#gift_choice_error'; 
        }else{
            window.location.hash = ''; 
        }
    });

    get_gift_object = function(gift){
        return $("#gift_"+gift.id);
    };
    
    gift_error = function(){
        $('#gift_choice_error').slideDown();
        window.gift_error_state=true
    };
    
    gift_error_reset = function(){
        $('#gift_choice_error').css({'display':'none'});
        window.gift_error_state=false
        
    };
    //marks a gift object as unavailable and disables its select
    mark_unavailable = function(gift_dict){
        gift=get_gift_object(gift_dict)
        //console.log('marking gift unavailable', gift);
        gift.addClass('unavailable');
        radio_button=gift.children().filter('.giftfoot').children().filter(':input').first();
        radio_button.prop('disabled', true );

        if(radio_button.prop('checked')){
            gift_error()
        }
    };
    //re-enables a gift choice
    mark_available = function(gift_dict){
        gift=get_gift_object(gift_dict);
        //console.log('marking gift available', gift);
        gift.removeClass('unavailable');
        radio_button=gift.children().filter('.giftfoot').children().filter(':input').first();
        radio_button.prop('disabled', false );
    };

    //main logic for figuring out which gift choices need updating 
    reflect_amount = function(amount, monthly){
        gift_error_reset();
        //console.log('reflecting the amount: ', amount, 'with monthly set to', monthly)
        for(index in giftset){
            gift=giftset[index]
            if(!monthly && (amount < gift.minimum_onetime)){
                mark_unavailable(gift);
            }else if(monthly && (amount < gift.minimum_monthly)){
                mark_unavailable(gift);
                
            }else{
                mark_available(gift);
            }
        }
    };
    refresh = function(){
        if( giftset != undefined){
            // amount radio select hooks
            if($("#id_other_0").prop('checked')){
                    amount= $('#id_other_onetime').val();
                    monthly=false;
            }else if($("#id_other_1").prop('checked')){
                    amount= $('#id_other_monthly').val();
                    monthly=true;
            }else{
                selected_amount=$(":input[name='amounts']").filter(':checked');
                amount= selected_amount.val()
                if( selected_amount.hasClass('monthly_choice')){
                    monthly=true;
                }else{
                    monthly=false;
                }
            }
            reflect_amount(amount, monthly);
        }
    };
    $(":input[name='giftchoice']").change(function(){refresh();});
    $(":input[name='other_amount']").filter('#id_other_onetime').keyup(function(){
        //console.log('other onetime');
        reflect_amount(this.value, false);
    });
    $(":input[name='other_amount']").filter('#id_other_monthly').keyup(function(){
        //console.log('other monthly');
        reflect_amount(this.value, true);
    });
    

    /*** Onetime ***/
    $('.onetime_choice').click(function() {
    	$('#id_donation_type').val('donate');
        refresh();
    });

    $('#id_other_0').click(function() {
        $('input[name=amounts]:checked').attr('checked', false);
        $('#id_other_onetime').attr('disabled', false);
        $('#id_other_onetime').focus();
        $('#id_other_monthly').attr('disabled', true);
        refresh();
     });    

    $('#id_other_onetime').focusin(function() {
        $('input[name=amounts]:checked').attr('checked', false);
        $('#id_other_onetime').attr('disabled', false);
        $('#id_other_onetime').focus();
        $('#id_other_monthly').attr('disabled', true);

        $("#id_other_0").attr("checked", true);
        $('.greenLabel').removeClass('greenLabel')
        $("label[for=id_other_0]").addClass("greenLabel");
        $('#id_donation_type').val('donate');
        refresh();
    });

    /*** Monthly other ***/
    $('.monthly_choice').click(function() {
    	$('#id_donation_type').val('subscribe');
        refresh();
    });

    $('#id_other_1').click(function() {
        $('input[name=amounts]:checked').attr('checked', false);
        $('#id_other_monthly').attr('disabled', false);
        $('#id_other_monthly').focus();
        $('#id_other_onetime').attr('disabled', true);
    });

    $('#id_other_monthly').focusin(function() {
        $('input[name=amounts]:checked').attr('checked', false);
        $('#id_other_monthly').attr('disabled', false);
        $('#id_other_monthly').focus();
        $('#id_other_onetime').attr('disabled', true);

        $('input[name=amounts]:checked').attr('checked', false);
        $("#id_other_1").attr("checked", true);
        $('.greenLabel').removeClass('greenLabel')
        $("label[for=id_other_1]").addClass("greenLabel");
        $('#id_donation_type').val('subscribe');
    });    

    /*** Generic ***/ 
    $('#sameshipping').click(function() {
        $("#shippingdetails").toggle();
    });
//    if( $('#id_phonenumber').val() == 'XXX-XXX-XXXX'){
//        $('#id_phonenumber').css({'color':'grey'});
//    };
//    $('#id_phonenumber').focus(function(){
//        if( $('#id_phonenumber').val() == 'XXX-XXX-XXXX'){
//            $('#id_phonenumber').val('').css({'color':'black'});
//        }
//    });
   
    if ($.cookie('csrftoken') === null){
    	$('#cookie-disabled-message').show();
    }

/*********/
    $('#one-time').change(function() {
    	if ( $(this).is(':checked')) {
    		$('#monthlyPrices').hide();
    		$('#one-timePrices').show();
    		$('#one-timePrices .greenLabel').removeClass('greenLabel')
    		$('.onetime_choice:first').attr('checked', true)
            $("input[type=radio]:checked + label").addClass("greenLabel");
    		$('#id_other_onetime').removeAttr('disabled')
    		$('#id_other_monthly').attr('disabled', 'true')
    	}
    });

    $('#monthly').change(function() {
    	if ( $(this).is(':checked')) {
    		$('#one-timePrices').hide();						
    		$('#monthlyPrices').show();
    		$('#monthlyPrices .greenLabel').removeClass('greenLabel')
    		$('.monthly_choice:first').attr('checked', true)
            $("input[type=radio]:checked + label").addClass("greenLabel");
    		$('#id_other_onetime').attr('disabled', 'true')
    		$('#id_other_monthly').removeAttr('disabled')
    	}
    });       

    //set the initial state
    //console.log('initial set up')
    //handle other amount being checked
    //
    if( giftset != undefined){
        if($(":input[name='other']").prop('checked')){
            initial_amount = $(":input[name='other_amount']").val();
        }else{
            initial_amount = $(":input[name='amounts']").filter(':checked').val();
        }
        if( $(":input[name='type']").val() == 'donate'){
            reflect_amount(initial_amount, false);
        }else{
            reflect_amount(initial_amount, true);
        };
    }
});
