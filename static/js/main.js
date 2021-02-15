var lastId = -1;
var Device_ID;
function update_messages(device_id)
{
    Device_ID = device_id;

	$.ajax({
    url: '/messages?last='+lastId + "&device=" + Device_ID,
    dataType : "json",

    success: function (data, textStatus) { 
        $.each(data, function(i, d)
		{    
			$("#table_event tr:first").after("<tr><td>"+d['user']+"</td><td>"+d['text']+"</td><td>"+d['datetime']+"</td></tr>");
			lastId = d['id']
        });
		//$("#div_body")[0].scrollTop = $("#div_body")[0].scrollHeight;
    } 
	});


	setTimeout(function(){ update_messages(Device_ID )},500);
}

function sendCmd(cmd, dev)
{
    $.ajax({
    url: '/cmd?cmd='+cmd + '&dev='+dev,
    success: function (data, textStatus) {
    }
	});
}
