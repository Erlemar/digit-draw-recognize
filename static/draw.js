var drawing = false;

var context;

var offset_left = 0;
var offset_top = 0;


function start_canvas ()
{
    var canvas = document.getElementById ("the_stage");
    context = canvas.getContext ("2d");
    canvas.onmousedown = function (event) {mousedown(event)};
    canvas.onmousemove = function (event) {mousemove(event)};
    canvas.onmouseup   = function (event) {mouseup(event)};
    for (var o = canvas; o ; o = o.offsetParent) {
    offset_left += (o.offsetLeft - o.scrollLeft);
    offset_top  += (o.offsetTop - o.scrollTop);
    }
    draw();
}

function getPosition(evt)
{
    evt = (evt) ?  evt : ((event) ? event : null);
    var left = 0;
    var top = 0;
    var canvas = document.getElementById("the_stage");

    if (evt.pageX) {
    left = evt.pageX;
    top  = evt.pageY;
    } else if (document.documentElement.scrollLeft) {
    left = evt.clientX + document.documentElement.scrollLeft;
    top  = evt.clientY + document.documentElement.scrollTop;
    } else  {
    left = evt.clientX + document.body.scrollLeft;
    top  = evt.clientY + document.body.scrollTop;
    }
    left -= offset_left;
    top -= offset_top;

    return {x : left, y : top}; 
}

function
mousedown(event)
{
    drawing = true;
    var location = getPosition(event);
    context.lineWidth = 8.0;
    context.strokeStyle="#000000";
    context.beginPath();
    context.moveTo(location.x,location.y);
}


function
mousemove(event)
{
    if (!drawing) 
        return;
    var location = getPosition(event);
    context.lineTo(location.x,location.y);
    context.stroke();
}



function
mouseup(event)
{
    if (!drawing) 
        return;
    mousemove(event);
	context.closePath();
    drawing = false;
}

function draw()
{

    context.fillStyle = '#ffffff';
    context.fillRect(0, 0, 200, 200);

}

function clearCanvas()
{
    context.clearRect (0, 0, 200, 200);
    draw();
    document.getElementById("rec_result").innerHTML = "";
}


function processImg()
{
	document.getElementById("rec_result").innerHTML = "connecting...";
    var canvas = document.getElementById ("the_stage");

    var imageData =  canvas.toDataURL('image/png');
    var dataTemp = imageData.substr(22);  

    var sendPackage = {"id": "1", "txt": dataTemp};
    $.post("/process", sendPackage, function(data){
        data = JSON.parse(data);
        if(data["status"] == 1)
        {
            document.getElementById("rec_result").innerHTML = data["result"];
        }
        else
        {
            document.getElementById("rec_result").innerHTML = "failed";
        }
    });
}


/*
function saveImg()
{
	document.getElementById("rec_result").innerHTML = "connecting3...";
	var dataURL = canvas.toDataURL('image/jpeg', 1.0);
	$.ajax({
		type: "POST",
		url: "save-canvas",
		data: { param: dataURL}
	}).done(function( o ) {
		save_img(dataURL)
		
	});
	document.getElementById("rec_result").innerHTML = "connecting4...";
}
*/

function saveImg()
{
	document.getElementById("rec_result").innerHTML = "connecting3...";
	var dataURL = canvas.toDataURL('image/jpeg', 1.0);
	$.ajax({
		type: "POST",
		url: "url",
		data: { param: dataURL}
	}).done(function( o ) {
		a = save_img(dataURL);
		
	});
	document.getElementById("rec_result").innerHTML = a;
}

function saveImg1()
{
	document.getElementById("rec_result").innerHTML = "connecting...";
	var canvas = document.getElementById("the_stage");
	var dataURL = canvas.toDataURL('image/jpg');
	var dig = document.querySelector('input[name="action"]:checked').value;
	$.ajax({
	  type: "POST",
	  url: "/hook",
	  data:{
		imageBase64: dataURL,
		digit: dig
		}
	}).done(function(response) {
	  console.log(response)
	  document.getElementById("rec_result").innerHTML = response
	});
	
}






onload = start_canvas;