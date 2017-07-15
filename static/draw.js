var drawing = false;

var context;

var offset_left = 0;
var offset_top = 0;

//canvas functions
function start_canvas () {
    var canvas = document.getElementById ("the_stage");
    context = canvas.getContext ("2d");
    canvas.onmousedown = function (event) {mousedown(event)};
    canvas.onmousemove = function (event) {mousemove(event)};
    canvas.onmouseup = function (event) {mouseup(event)};
    canvas.ontouchstart = function (event) {touchstart(event)};
    canvas.ontouchmove = function (event) {touchmove(event)};
    canvas.ontouchend = function (event) {touchend(event)};
    for (var o = canvas; o ; o = o.offsetParent) {
		offset_left += (o.offsetLeft - o.scrollLeft);
		offset_top  += (o.offsetTop - o.scrollTop);
    }
    draw();
}

function getPosition(evt) {
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

function getTouchPos(e) {
	if (!e)
		var e = event;
	var touchX = 0;
	var touchY = 0;

	if(e.touches) {
		if (e.touches.length == 1) { // Only deal with one finger
			var touch = e.touches[0]; // Get the information for finger #1
			touchX=touch.pageX-touch.target.offsetLeft;
			touchY=touch.pageY-touch.target.offsetTop;
		}
	}
	return {x : touchX, y : touchY}
}

function mousedown(event) {
    drawing = true;
    var location = getPosition(event);
    context.lineWidth = 8.0;
    context.strokeStyle="#000000";
    context.beginPath();
    context.moveTo(location.x,location.y);
}

function touchstart(event) {
    drawing = true;
    var location = getTouchPos();
    context.lineWidth = 8.0;
    context.strokeStyle="#000000";
    context.beginPath();
    context.moveTo(location.x,location.y);
	//event.preventDefault();
}

function mousemove(event) {
    if (!drawing) 
        return;
    var location = getPosition(event);
    context.lineTo(location.x,location.y);
    context.stroke();
}

function touchmove(event) {
    if (!drawing) 
        return;
    var location = getTouchPos(event);
    context.lineTo(location.x,location.y);
    context.stroke();
	//event.preventDefault();
}


function mouseup(event) {
    if (!drawing) 
        return;
    mousemove(event);
	context.closePath();
    drawing = false;
}

function touchend(event) {
    if (!drawing) 
        return;
    touchmove(event);
	context.closePath();
    drawing = false;
}

function draw() {
    context.fillStyle = '#ffffff';
    context.fillRect(0, 0, 200, 200);
}

function clearCanvas() {
    context.clearRect (0, 0, 200, 200);
    draw();
    document.getElementById("hide_show_btn").style.display = "none";
    document.getElementById("prediction").style.display = "none";
    document.getElementById("hidable").style.display = "none";
    document.getElementById("answer_reaction").innerHTML = "";
    document.getElementById("rec_result").innerHTML = "";
}

//button events
function hide_show() {
    var x = document.getElementById('hidable');
    if (x.style.display === 'none') {
        x.style.display = 'block';
		document.getElementById("hide_show_btn").innerHTML = 'Hide detailed information'
    } else {
        x.style.display = 'none';
		document.getElementById("hide_show_btn").innerHTML = 'Show detailed information'
    }
}


function positive_pred() {
	if (document.getElementById("Checkbox").checked == true) {
		document.getElementById("answer_reaction").innerHTML = "Great! Thank you, the digit will be used to improve the models further.";
		document.getElementById("prediction").style.display = "none";
		var digit = document.getElementById("rec_result").innerHTML;
		var trained = train_model(digit);
		console.log(trained)
	} else {
		document.getElementById("answer_reaction").innerHTML = "Cool! The app works, but you could help improving it by checking the box next time.";
		document.getElementById("prediction").style.display = "none";
	}
}

function negative_pred() {
	if (document.getElementById("Checkbox").checked == true) {
		document.getElementById("answer_reaction").innerHTML = "This was an error! Could you please choose the correct number and submit it?";
		document.getElementById("prediction").style.display = "none";
		document.getElementById("digit_form").style.display = "block";	
	} else {
		document.getElementById("answer_reaction").innerHTML = "A pity :( If only the models could use this image to correct the error...";
		document.getElementById("prediction").style.display = "none";
	}
}



function predict() {
	document.getElementById("digit_form").style.display = "none";	
	document.getElementById("rec_result").innerHTML = "Predicting...";
	document.getElementById("prediction").style.display = "block";
	document.getElementById("hide_show_btn").style.display = 'block';
	document.getElementById("answer_reaction").innerHTML = "";

	if (document.getElementById("hide_show_btn").innerHTML == 'Hide detailed information') {
		document.getElementById("hidable").style.display = "block";
	} else {
		document.getElementById("hidable").style.display = "none";
	}	
	var canvas = document.getElementById("the_stage");
	var dataURL = canvas.toDataURL('image/jpg');
	
	$.ajax({
		type: "POST",
		url: "/hook2",
		data:{
			imageBase64: dataURL
		}
	}).done(function(response) {
		console.log(response)
		if (response == "Can't predict, when nothing is drawn") {
			document.getElementById("hide_show_btn").style.display = "none";
			document.getElementById("prediction").style.display = "none";
			document.getElementById("hidable").style.display = "none";
			document.getElementById("answer_reaction").innerHTML = "";
		} else {
			//answers = response
			document.getElementById("prediction").style.display = "block";
			document.getElementById("hide_show_btn").style.display = 'block';
			document.getElementById("answer_reaction").innerHTML = "";
		}
		var response = JSON.parse(response)
		//answer, top_3, top_3_original, top_3_cnn, top_3_cnn_original

		document.getElementById("fnn1").innerHTML = response['fnn'][0];
		document.getElementById("fnn2").innerHTML = response['fnn'][1];
		document.getElementById("fnn3").innerHTML = response['fnn'][2];
		document.getElementById("fnn_t1").innerHTML = response['fnn_t'][0];
		document.getElementById("fnn_t2").innerHTML = response['fnn_t'][1];
		document.getElementById("fnn_t3").innerHTML = response['fnn_t'][2];
		document.getElementById("cnn1").innerHTML = response['cnn'][0];
		document.getElementById("cnn2").innerHTML = response['cnn'][1];
		document.getElementById("cnn3").innerHTML = response['cnn'][2];
		document.getElementById("cnn_t1").innerHTML = response['cnn_t'][0];
		document.getElementById("cnn_t2").innerHTML = response['cnn_t'][1];
		document.getElementById("cnn_t3").innerHTML = response['cnn_t'][2];
		document.getElementById("rec_result").innerHTML = response["answer"];
	});
}

function submit_correct_digit()
{
	var digit = document.getElementById("digits");
	var correct_digit = digit.options[digit.selectedIndex].text
	document.getElementById("digit_form").style.display = "none";
	document.getElementById("answer_reaction").innerHTML = "Thank you! The models should work better now.";
	
	var trained = train_model(correct_digit);
	console.log(trained)

}

function train_model(digit) {
	var digit = digit;
	var canvas = document.getElementById("the_stage");
	var dataURL = canvas.toDataURL('image/jpg');
	document.getElementById("rec_result").innerHTML = 'Training...'
	$.ajax({
		type: "POST",
		url: "/hook3",
		data:{
			digit: digit,
			imageBase64: dataURL
		}
	}).done(function(response) {
	  console.log(response)
	  document.getElementById("rec_result").innerHTML = response
	});
}


onload = start_canvas;

// https://stackoverflow.com/questions/16057256/draw-on-a-canvas-via-mouse-and-touch
// https://bencentra.com/code/2014/12/05/html5-canvas-touch-events.html