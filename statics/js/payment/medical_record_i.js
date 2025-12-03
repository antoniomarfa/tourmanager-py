var public_vars = public_vars || {};

"use strict";

$(document).ready(function () {

	// Radio Toggle
	if ($.isFunction($.fn.bootstrapSwitch)) {

		$('.make-switch.is-radio').on('switch-change', function () {
			$('.make-switch.is-radio').bootstrapSwitch('toggleRadioState');
		});
	}

	$('#comuna_id').select2({
		placeholder: 'Seleccione una comuna',
	});

	$('#region_id').select2({
		placeholder: 'Seleccione una region',
	});
});
