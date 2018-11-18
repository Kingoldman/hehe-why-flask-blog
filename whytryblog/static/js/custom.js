$(function () {
    function render_time() {
        return moment($(this).data('timestamp')).format('lll')
    }
    $('[data-toggle="tooltip"]').tooltip(
        {title: render_time}
    );
});

 $(function() {
	var scrollDiv = document.createElement('div');
	 $(scrollDiv).attr('id', 'toTop').html('返回顶部').appendTo('body');
	  $(window).scroll(function() {
	      if ($(this).scrollTop() != 0) {
	          $('#toTop').fadeIn(1000);
	      } else {
	          $('#toTop').fadeOut(1000);
	      }
	 });
	 $('#toTop').click(function() {
	     $('body,html').animate({ scrollTop: 0 }, 200);
	        })
});