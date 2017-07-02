$(document).ready( function(){

	// $('#addchar-submit').on('click', function() {
	// 	$('#addchar-input').val('');
	// }

	$('.addchar-options-group').hide()
	$('#addchar-input').on('input', function (){
		var zkillAutocompleteUrl = "https://zkillboard.com/autocomplete/characterID/";
		var searchUrl = zkillAutocompleteUrl+$(this).val();
		console.log(searchUrl)
		$.ajax(searchUrl, {
			'success': function(data) {
				if (data.length) {
					$('.addchar-options-group').show()
					$('#addchar-options').empty()
					data.forEach( function(charInfo){
						var charTab = $('<div></div>',{class:'col-md-4'})
						var portrait = $('<img>',{src:'https://imageserver.eveonline.com/'+charInfo.image});
						var name = $('<button></button>',{
							class:'character-option btn',
							'data-toggle':'modal',
							'data-target':'#addchar-modal',
							'data-character':charInfo.id
						})
						name.append(portrait,charInfo.name);
						charTab.append(name);
						name.on('click', function(){
							$('#addchar-modal-body').html($(this).html());
							$('#character-to-add').val($(this).attr('data-character'));
						});
						$('#addchar-options').append(charTab);
					});
				} else {
					$('.addchar-options-group').hide();
				}			
			},
			'error': function(err) {
				console.log('error',err);
			}
		})
	});
});