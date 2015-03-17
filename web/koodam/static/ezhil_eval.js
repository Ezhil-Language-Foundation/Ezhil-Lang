/* (C) 2013 Muthiah Annamalai */


var aceEditor = null;

function appendText( text_elements  ) {
    require(["ace/ace"], function(ace) {
        var editor = ace.edit("editor");
        if ( editor ) {
            editor.insert( text_elements ); //insert at cursor
        } else {
            $("#editor").html( text_elements );
        }
    })
}

function getEzhilCookie(name)  {
    var value = document.cookie;

    //try the two alternatives
    var start = value.indexOf(" " + name + "=");
    if ( start == -1)  {
        start = value.indexOf(name + "=");
    }
    if ( start == -1) {
        return null;
    }

    //now find the start-end positions in substrings
    start = value.indexOf("=", start) + 1;
    var end = value.indexOf(";", start);
    if ( end == -1) {
        end = value.length;
    }

    //find and unescape the relevant part of the cookie stuff
    value = unescape( value.substring(start,end));
    
    return value;
}

function setEzhilCookie( name, program )
{
    var expiry_date = new Date();
    expiry_date.setDate(expiry_date.getDate() + 7); /* 7-day expiry */      
    document.cookie = name + "=" +escape(program)+"; expires="+expiry_date.toUTCString();
}

function checkEzhilCookie()
{
    var program = getEzhilCookie("program");
    if ( program != null && program != "") {
        /** alert("I remember you, and your program!")
            alert(program); */
        if ( aceEditor != null ) {
            aceEditor.setValue(program);
            aceEditor.clearSelection();
        }
    }
    else {
        /**  alert("Cookie not found, or no cookie set yet!"); */
    }
}

require.config({
    baseUrl: "/",
    paths: {
        ace: "static/ace"
    }
});


//evaluate on-load - check cookie and populate the editor field if we were here before.
require(["ace/ace"], function(ace) {
    var editor = ace.edit("editor");
    if ( editor ) {
        aceEditor = editor;
    editor.setTheme("ace/theme/xcode");
    editor.getSession().setMode("ace/mode/ezhil");
        editor.setValue($("#default_program").html());
    checkEzhilCookie();
    } else {
        $("#editor").html( $("#default_program").html() )
    }
});

function evaluateProg() {  
    if ( aceEditor == null ) {
        alert("editor could not be loaded! cannot evaluate program");
        return null;
    }
    /* Save program as cookie */        
    setEzhilCookie("program",aceEditor.getValue());
    
    output = window.open( "","Ezhil evaluator output","width=700,height=400,scrollbars=yes");
    $('<form>', {
        "id": 'EvaluateProgramForm',
        "html": '<input type="hidden" name="eval" value="true" /><textarea rows="20" cols="80" id="EzhiCodeWidget" name="prog">' + aceEditor.getValue() + '</textarea><input type="submit" label="submit" />'  ,
        "action": "/play/eval/",
        "method":"POST"
    }).appendTo(output.document.body).submit();
}

function updateEditorWithExample( filename ) {

    $.ajax({
        url: "/static/ezhil_tests/"+filename,
        cache: false
    }).done(function( program ) {
        if ( aceEditor == null ) {
            alert("editor could not be loaded! cannot show requested demo"+$("#examples").val())
            $("#editor").html( program );
        } else {
            aceEditor.setValue( program );
            aceEditor.clearSelection();
        }
    });
}

// inline output
function ezhilPostEval(  ) {
    //1. on callback return display success
    var ezhilPostEval_update_widget = function ( raw_data )  {
	var dataObj = JSON.parse( raw_data );
	var data = dataObj["program_output"];
	var did_it_fail = dataObj["failed_flag"];
	var pre_data = "<pre>\n"+data +"</pre>";
        if ( aceEditor == null ) {
            alert("editor could not be loaded! cannot show requested demo"+$("#examples").val())
            $("#EzhilOutput").html( pre_data);
        } else {
            $("#EzhilOutput").html( pre_data );
        }
	
	if ( did_it_fail ) {
	    //failed
	    $("#EzhilOutput").css( "background-color","red");
	} else {
	    //success
	    $("#EzhilOutput").css( "background-color","yellow");
	}
    };
    
    //0. make the call
    $("#EzhilOutput").html("<b> Processing request; please wait ... ... ... ... .. .");

    $.ajaxSetup({
	beforeSend: function(xhr, settings) {
	    xhr.setRequestHeader("X-CSRFToken", getEzhilCookie('csrftoken'));
	}
    });

    $.ajax({
	type:"POST",
	url:"/play/eval/",
	data: {"eval":true,"prog":aceEditor.getValue()},
	success:ezhilPostEval_update_widget});
}

/* Currently web-based evaluator works only in FireFox */
function showDisclaimer() {
    var isMozillaBased = navigator.userAgent.search("Mozilla") >= 0 && !(navigator.userAgent.search("Chrome") >= 0);
    if ( ! isMozillaBased ) {
        $("#disclaimer").show();
    }
    return false;
}

$.ready(showDisclaimer);
$.ready(function () { aceEditor.clearSelection() });

