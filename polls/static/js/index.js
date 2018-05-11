jQuery(document).ready(function() {

    $('table > tbody > tr').click(function() {
        var href = $(this).find("a").attr("href");
        if(href) {
            window.location = href;
        }
    });

});
