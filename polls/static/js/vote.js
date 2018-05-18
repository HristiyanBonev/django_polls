
$(function() {
    $('.answer-list input[type="radio"]').each(function(index) {
        console.log($(this));
        $(this).attr('id', 'radio' + index);
        var label = $('<label />', {'for': 'radio' + index}).html($(this).parent().html());
        $(this).parent().empty().append(label);
    });
    $('label').click(function () {
       $('label').removeClass('selected');
       $(this).addClass('selected');
    });
});
