// Enter your imgbb api key below 

var apikey = "";


/*  ==========================================
    SHOW UPLOADED IMAGE
* ========================================== */
function readURL(input) {
    console.log("readURL function...");
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            $('#imageResult')
                .attr('src', e.target.result);
        };
        reader.readAsDataURL(input.files[0]);
    }
}

$(function () {
    $('#upload').on('change', function () {
        readURL(input);
        uploadimage('upload')
    });
});


/*  ==========================================
    SHOW UPLOADED IMAGE NAME
* ========================================== */
var input = document.getElementById( 'upload' );
//var infoArea = document.getElementById( 'upload-label' ); #TODO: causes null value exception
var urllink = document.getElementById( 'urllink' );


input.addEventListener( 'change', showFileName );

function showFileName( event ) {
    console.log("showFileName function...");
    var input = event.srcElement;
    var fileName = input.files[0].name;
    //infoArea.textContent = 'File name: ' + fileName; #TODO: causes null value exception
}

function uploadimage(input_tag) {
	console.log("uploadimage function...");
	var file = document.getElementById(input_tag);
	var form = new FormData();
	form.append("image", file.files[0])
	$('#save_profile').prop('disabled', true);

	var settings = {
		//"url": "https://api.imgbb.com/1/upload?key="+apikey,
		"url": "/add_image",
		"method": "POST",
		"timeout": 0,
		"processData": false,
		"mimeType": "multipart/form-data",
		"contentType": false,
		"data": form
	};


	console.log('calling add image');
	$.ajax(settings).done(function (response) {
		console.log('done calling add image');
		var res = JSON.parse(response);
		if(res.success) {
			toastr.success(res.message);
			$('#profile_image_name').val(res.profile_image_name);
			$('#save_profile').prop('disabled', false);
		} else {
			toastr.error(res.message);
		}
		console.log(response);
		//var jx = JSON.parse(response);
		//console.log(jx.data.url);
		//urllink.innerHTML = jx.data.url ;
	});
}

$(document).on('click','#save_profile',function(){
    form = new FormData($('#application-form')[0]);
    $('#save_profile').prop('disabled', true);
    var ch_data = [];
    $('input[type="checkbox"]:checked').each(function(){
        ch_data.push($(this).attr('value'));
    });
    form.append('properties',ch_data);
    $.ajax({
        processData: false,
        contentType: false,
        type: "POST",
        url: "/store_profile",
        data: form,
        success: function (data) {
            res = JSON.parse(data);
            if(res.success) {
                toastr.success(res.message);
                window.location = '/admin_profiles'
            }
            else {
                toastr.error(res.message);
            }
            $('#save_profile').prop('disabled', false);
        },
        error: function (error) {
            toastr.error("Sorry, There is an error in ajax call");
            $('#save_profile').prop('disabled', false);
        }
    });

});

$(document).on('dragstart dragenter dragover', function(event) {    
        $('#image-drag-drop').removeClass('d-none');     // Show the drop zone
    dropZoneVisible= true;
    
}).on('drop dragleave dragend', function (event) {

    
    dropZoneTimer= setTimeout( function(){
        if( !dropZoneVisible ) {
            $('#image-drag-drop').addClass('d-none'); 
        }
    }, 50   ); // dropZoneHideDelay= 70, but anything above 50 is better
    clearTimeout(dropZoneTimer);
        

});
