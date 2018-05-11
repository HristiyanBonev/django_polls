//made by Hristiyan Bonev - 11.05.2018

function cloneMore(type) {
  // This function adds text input elements on clicking 'Add choice button'
  // in "Add Question" page. There are detailed comments aside.
    var newElement = $('#empty_form').clone(true);                            //copying the hidden form
    var total = $('#id_' + type + '-TOTAL_FORMS').val();                      //calculates the current total forms (before adding)
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
    newElement.css('display','block')                                         //removing the display:none
    newElement.removeAttr('id')                                               //removing 'empty_form' ID
    total++;                                                                  //incrementing the total
    $('#id_' + type + '-TOTAL_FORMS').val(total);                             //increasing the TOTAL_FORMS field with 1 for each created input field

    $($('#add_button')).before(newElement);                                   // inserting the newly created input field after the last input field
}
}
