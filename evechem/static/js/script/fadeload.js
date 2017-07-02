// $(".fade-on-load").each(function(){
//     if (!this.complete) {
//         $(this).on("load", function () {
//         	console.log('fading in')
//             $(this).fadeIn();
//         });
//     } else {
//         $(this).fadeIn();
//     }
// });

$(document).ready(function(){
	// $(".fade-on-load").fadeIn();
	$(".fade-on-load").each(function(){
    if (!this.complete) {
        $(this).on("load", function () {
        	console.log('fading in')
            $(this).fadeIn();
        });
    } else {
        $(this).fadeIn();
    }
});
	$('#header-content').css('opacity','1');
});