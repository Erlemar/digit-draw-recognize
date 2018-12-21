//for canvas drawing used code from here: https://github.com/zealerww/digits_recognition/blob/master/digits_recognition/static/draw.js
var drawing = false;

var context;

var offset_left = 0;
var offset_top = 0;

function startup() {
  var el = document.body;
  el.addEventListener("touchstart", handleStart, false);
  el.addEventListener("touchend", handleEnd, false);
  el.addEventListener("touchcancel", handleCancel, false);
  el.addEventListener("touchleave", handleEnd, false);
  el.addEventListener("touchmove", handleMove, false);
}


//canvas functions
function start_canvas () {
    var canvas = document.getElementById("the_stage");
    context = canvas.getContext("2d");
    //document.getElementById("the_stage").style.display = "none";
    canvas.onmousedown = function (event) {mousedown(event)};
    canvas.onmousemove = function (event) {mousemove(event)};
    canvas.onmouseup = function (event) {mouseup(event)};
    canvas.onmouseout = function (event) {mouseup(event)};
    canvas.ontouchstart = function (event) {touchstart(event)};
    canvas.ontouchmove = function (event) {touchmove(event)};
    canvas.ontouchend = function (event) {touchend(event)};
    for (var o = canvas; o ; o = o.offsetParent) {
		offset_left += (o.offsetLeft - o.scrollLeft);
		offset_top  += (o.offsetTop - o.scrollTop);
    }

	var el =document.body;
	el.addEventListener("touchstart", handleStart, false);
	el.addEventListener("touchend", handleEnd, false);
	el.addEventListener("touchcancel", handleCancel, false);
	el.addEventListener("touchleave", handleEnd, false);
	el.addEventListener("touchmove", handleMove, false);
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


function mousedown(event) {
    drawing = true;
    var location = getPosition(event);
    context.lineWidth = 8.0;
    context.strokeStyle = "#000000";
    context.beginPath();
    context.moveTo(location.x, location.y);
}


function mousemove(event) {
    if (!drawing)
        return;
    var location = getPosition(event);
    context.lineTo(location.x, location.y);
    context.stroke();
}


function mouseup(event) {
    if (!drawing)
        return;
    mousemove(event);
	context.closePath();
    drawing = false;
}


function draw() {
    context.fillStyle = '#ffffff';
    context.fillRect(0, 0, 200, 200);
}

//Used mozilla docs for this code https://developer.mozilla.org/en-US/docs/Web/API/Touch_events
var ongoingTouches = new Array;
function handleStart(evt) {

	var canvas = document.getElementById("the_stage");
	var context = canvas.getContext("2d");
	var touches = evt.changedTouches;
	var offset = findPos(canvas);


	for (var i = 0; i < touches.length; i++) {
		if(touches[i].clientX-offset.x >0 && touches[i].clientX - offset.x < parseFloat(canvas.width) && touches[i].clientY - offset.y > 0 && touches[i].clientY - offset.y < parseFloat(canvas.height)){
			evt.preventDefault();
			ongoingTouches.push(copyTouch(touches[i]));
			context.beginPath();
			//context.arc(touches[i].clientX - offset.x, touches[i].clientY - offset.y, 4, 0, 2 * Math.PI, false); // a circle at the start
			context.fillStyle = "#000000";
			context.fill();
		}
	}
}
function handleMove(evt) {

	var canvas = document.getElementById("the_stage");
	var context = canvas.getContext("2d");
	var touches = evt.changedTouches;
	var offset = findPos(canvas);

	for (var i = 0; i < touches.length; i++) {
        if(touches[i].clientX-offset.x > 0 && touches[i].clientX-offset.x < parseFloat(canvas.width) && touches[i].clientY-offset.y > 0 && touches[i].clientY - offset.y < parseFloat(canvas.height)){
              evt.preventDefault();
			var idx = ongoingTouchIndexById(touches[i].identifier);

			if (idx >= 0) {
				context.beginPath();
				context.moveTo(ongoingTouches[idx].clientX - offset.x, ongoingTouches[idx].clientY - offset.y);

				context.lineTo(touches[i].clientX - offset.x, touches[i].clientY - offset.y);
				context.lineWidth = 4;
				context.strokeStyle = "#000000";
				context.stroke();

				ongoingTouches.splice(idx, 1, copyTouch(touches[i])); // swap in the new touch record
			} else {
			}
		}
    }
}
function handleEnd(evt) {

	var canvas = document.getElementById("the_stage");
	var context = canvas.getContext("2d");
	var touches = evt.changedTouches;
	var offset = findPos(canvas);

	for (var i = 0; i < touches.length; i++) {
		if(touches[i].clientX-offset.x > 0 && touches[i].clientX-offset.x < parseFloat(canvas.width) && touches[i].clientY-offset.y > 0 && touches[i].clientY-offset.y < parseFloat(canvas.height)){
			evt.preventDefault();
			var idx = ongoingTouchIndexById(touches[i].identifier);

			if (idx >= 0) {
				context.lineWidth = 4;
				context.fillStyle = "#000000";
				context.beginPath();
				context.moveTo(ongoingTouches[idx].clientX - offset.x, ongoingTouches[idx].clientY - offset.y);
				context.lineTo(touches[i].clientX - offset.x, touches[i].clientY - offset.y);
				//context.fillRect(touches[i].clientX - 4 -offset.x, touches[i].clientY - 4 - offset.y, 8, 8); // and a square at the end
				ongoingTouches.splice(i, 1); // remove it; we're done
				} else {
			}
		}
    }
}
function handleCancel(evt) {
	evt.preventDefault();
	var touches = evt.changedTouches;

	for (var i = 0; i < touches.length; i++) {
		ongoingTouches.splice(i, 1); // remove it; we're done
	}
}

function copyTouch(touch) {
	return {identifier: touch.identifier,clientX: touch.clientX,clientY: touch.clientY};
}
function ongoingTouchIndexById(idToFind) {
	for (var i = 0; i < ongoingTouches.length; i++) {
		var id = ongoingTouches[i].identifier;

		if (id == idToFind) {
			return i;
		}
	}
	return -1; // not found
}

function findPos (obj) {
    var curleft = 0,
        curtop = 0;

    if (obj.offsetParent) {
        do {
            curleft += obj.offsetLeft;
            curtop += obj.offsetTop;
        } while (obj = obj.offsetParent);

        return { x: curleft - document.body.scrollLeft, y: curtop - document.body.scrollTop };
    }
}


function clearCanvas() {
    context.clearRect (0, 0, 200, 200);
    draw();
    document.getElementById("hide_show_btn").style.display = "none";
    document.getElementById("prediction").style.display = "none";
    document.getElementById("hidable").style.display = "none";
	document.getElementById("digit_form").style.display = "none";
    document.getElementById("answer_reaction").innerHTML = "";
    document.getElementById("rec_result").innerHTML = "";
	document.getElementById("a1").style.color = 'gray';
	document.getElementById("a2").style.color = 'gray';
	document.getElementById("a3").style.color = 'gray';
	document.getElementById("a4").style.color = 'gray';
	document.getElementById("a5").style.color = 'gray';
	document.getElementById("a6").style.color = 'gray';
	document.getElementById("a7").style.color = 'gray';
	document.getElementById("a8").style.color = 'gray';a1}

//button events
function hide_show() {
    var x = document.getElementById('hidable');
    if (x.style.display === 'none') {
        x.style.display = 'block';
		document.getElementById("hide_show_btn").innerHTML = 'Hide info'
    } else {
        x.style.display = 'none';
		document.getElementById("hide_show_btn").innerHTML = 'Show info'
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

function nothing() {
	document.getElementById("prediction").style.display = "none";
	document.getElementById("answer_reaction").innerHTML = "Well, the models on this site can recognize only digits... But you can draw anything, if you like :)";
}

function predict() {
	document.getElementById("digit_form").style.display = "none";
	document.getElementById("hidable").style.display = "none";
	document.getElementById("a1").style.color = 'gray';
	document.getElementById("a2").style.color = 'gray';
	document.getElementById("a3").style.color = 'gray';
	document.getElementById("a4").style.color = 'gray';
	document.getElementById("a5").style.color = 'gray';
	document.getElementById("a6").style.color = 'gray';
	document.getElementById("a7").style.color = 'gray';
	document.getElementById("a8").style.color = 'gray';
	document.getElementById("rec_result").innerHTML = "Predicting...";
	document.getElementById("prediction").style.display = "none";

	if (document.getElementById("hide_show_btn").innerHTML == 'Hide info') {
		document.getElementById("hidable").style.display = "block";
	} else {
		document.getElementById("hidable").style.display = "none";
	}
	var canvas = document.getElementById("the_stage");
	var dataURL = canvas.toDataURL('image/jpg');
	var t = document.getElementById("text").value;

	$.ajax({
		type: "POST",
		url: "/hook2",
		data:{
			text_data: t
		}
	}).done(function(response) {
		console.log(response)
		if (response == "Can't predict, when nothing is drawn") {
			document.getElementById("hide_show_btn").style.display = "none";
			document.getElementById("prediction").style.display = "none";
			document.getElementById("hidable").style.display = "none";
			document.getElementById("answer_reaction").innerHTML = "";
			document.getElementById("rec_result").innerHTML = response;
		} else {
			//answers = response
			document.getElementById("prediction").style.display = "block";
			document.getElementById("hide_show_btn").style.display = 'block';
			document.getElementById("answer_reaction").innerHTML = "";
			var response = JSON.parse(response);
			//answer, top_3, top_3_original, top_3_cnn, top_3_cnn_original

			document.getElementById("a1").style.color = 'black';
			document.getElementById("a2").style.color = 'black';
			document.getElementById("a3").style.color = 'black';
			document.getElementById("a4").style.color = 'black';
			document.getElementById("a5").style.color = 'black';
			document.getElementById("a6").style.color = 'black';
			document.getElementById("a7").style.color = 'black';
			document.getElementById("a8").style.color = 'black';

			document.getElementById("a1").innerHTML = response['channel'];
			document.getElementById("a2").innerHTML = response['id'];
			document.getElementById("a3").innerHTML = response['full_text'];
			document.getElementById("a4").innerHTML = response['agents'];
			document.getElementById("a5").innerHTML = response['master'];
			document.getElementById("a6").innerHTML = response['date_created'];
			document.getElementById("a7").innerHTML = response['date_transfer'];
			document.getElementById("a8").innerHTML = response['region'];
			document.getElementById("rec_result").innerHTML = response['found_count'];
		}
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