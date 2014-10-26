function validateForm(formName, inputs)
{
    for(var i = 0; i < inputs.length; i ++)
    {
        var x = document.forms[formName][inputs[i]].value;
        if (x==null || x=="") {
            alert("All fields must be filled out");
            return false;
        }
    }
}