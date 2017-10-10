
jQuery(document).ready(function() {
	
    /*
        Background slideshow
    */
    $('.c-form-container').backstretch("static/assets/img/backgrounds/bg.jpg");
    
    /*
        Wow
    */
    new WOW().init();
    
    /*
	    Contact form
	*/
	$('.c-form-box form').submit(function(e) {
		e.preventDefault();
		var this_form_parent = $(this).parents('.c-form-box');
	    var postdata = $(this).serialize();
	    $.ajax({
	        type: 'POST',
	        url: '/timetable',
	        data: postdata,
	        dataType: 'json',
	        success: function(json) {	            
	            
	        	$('.c-form-box form label[for="c-form-message"] .contact-error').fadeOut('fast', function(){
	        		if(json.messageMessage != '') {
		                $(this).html('(' + json.messageMessage + ')').fadeIn('fast');
		            }
	        	});
	            if(json.nameMessage == '' && json.emailMessage == '' && json.subjectMessage == '' && json.messageMessage == '') {
	            	this_form_parent.find('.c-form-top').fadeOut('fast');
	            	this_form_parent.find('.c-form-bottom').fadeOut('fast', function() {
	            		this_form_parent.append('<p>Thanks for contacting us! We will get back to you very soon.</p>');
	            		// reload background
	    				$('.c-form-container').backstretch("resize");
	                });
	            }
	            
	        }
	    });
	});
	
	
});
