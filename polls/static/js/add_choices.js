//made by Hristiyan Bonev - 11.05.2018

function cloneMore(type) {
  // Adds input box in "Add Question" page.
    var newElement = $('#empty_form').clone(true);//copying the hidden form
    var total = $('#id_' + type + '-TOTAL_FORMS').val();
    if (total < 5){
      newElement.find(':input').each(function() {                             //replacing __prefix__ with total (in input field ID)
        var name = $(this).attr('name').replace('__prefix__',total);
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id}).val('')
      });

      newElement.find('label').each(function() {                              // Also it does the same with the label for that input field
        var newFor = $(this).attr('for').replace('__prefix__', total);
        $(this).attr('for', newFor);
      });
    newElement.css('display','block')
    newElement.removeAttr('id')
    total++;
    $('#id_' + type + '-TOTAL_FORMS').val(total);                             //increasing the TOTAL_FORMS field with 1 for each created input field

    $($('#add_button')).before(newElement);                                   // inserting the newly created input field after the last input field
}
}
