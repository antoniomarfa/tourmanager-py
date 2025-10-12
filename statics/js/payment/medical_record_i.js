var public_vars = public_vars || {};

;(function($, window, undefined){

	"use strict";

	$(document).ready(function()
	{

// Radio Toggle
		if($.isFunction($.fn.bootstrapSwitch))
		{

			$('.make-switch.is-radio').on('switch-change', function () {
		        $('.make-switch.is-radio').bootstrapSwitch('toggleRadioState');
		    });
		}

    });
})    