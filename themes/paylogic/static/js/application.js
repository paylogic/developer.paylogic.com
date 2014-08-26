(function($){

    var smoothScrollElems = $('.reference.internal');
    var sticky = $('.uk-navbar[data-uk-sticky]');
    var stickyHeight;

    smoothScrollElems.each(function () {
        var element = $(this);
        stickyHeight = sticky.outerHeight();
        element.uk('smoothScroll', {
            'offset': stickyHeight + 10
        });
    });

})(jQuery);
