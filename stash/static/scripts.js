
    function validate_form_new(form){
        var inputs = [
            $(form).find("input[name=token]"),
            $(form).find("input[name=name]"),
            $(form).find("input[name=remote]"),
            $(form).find("input[name=type]"),
            $(form).find("textarea[name=description]")
        ];
        var result = true;

        $.each(inputs, function(index, value){
            if($(value).val() == ""){
                $(value).addClass('border-error');
                result = false;
            }
            else
                $(value).removeClass('border-error');
        });

        return result;
    }