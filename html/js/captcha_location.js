
let canvas, ctx;
let objX, objY, objW, objH;
let dragging = false;
let captcha_uuid;

let interval_id = 0;
let experiment_num = 10;
let captcha_cnt = 0;

$("#picker").spectrum({
      color: "#000000", // Initial Value
	  preferredFormat: "rgb"
	  
});


$('#start_button').on('click',function(){
    
    if(captcha_cnt >= experiment_num){
      alert("CAPTCHA test is done!");
      return;
    }

    $.ajax({
        url: 'http://127.0.0.1:8080/challenge',
        type: 'POST',
        dataType: 'json',
        timeout: 5000,
	})

    .done(function(data,textStatus,jqXHR){

		$('#title').show();
		$('#square').show();
		$('#captcha').show();

		img_number = data["img_num"];
		img_number3 = img_number.slice(0,3)
		console.log(img_number3);

		var square = document.getElementById("square");

		form = $("#captcha_form");


        canvas = $("#captcha_canvas")[0];
        ctx = canvas.getContext("2d");
        canvas.addEventListener('mousedown', onDown, false);
        canvas.addEventListener('mousemove', onMove, false);
        canvas.addEventListener('mouseup', onUp, false);
        objW = 5;
        objH = 5;
        objX = Math.floor(Math.random()*(canvas.width-objW));
        objY = Math.floor(Math.random()*(canvas.height-objH));
        var img = new Image();
        img.onload = function(){
            
            if(canvas.getContext){

                if(objX + objW > canvas.width){
                  objX = canvas.width - objW;
                }

                if(objY + objH > canvas.height){
                  objY = canvas.height - objH;
                }

                if(interval_id != 0)
                {
                  clearInterval(interval_id);
                }

                setForm();
		//drawRect四角形描画
                const drawRect = img => {
                    ctx.clearRect(0,0,canvas.width,canvas.height);
                    ctx.drawImage(img,0,0);
		    //ctx.drawImage(image, dx, dy, dWidth, dHeight)
                    ctx.globalAlpha = 1; //透明度
                    ctx.strokeRect(objX,objY,objW,objH);
                }
                interval_id = setInterval(function(){drawRect(img)},50);
            }
        }
        img.src = "data:image/png;base64," + data["blob"];
		    captcha_uuid = data["uuid"];
        console.log(data["color"])
        square.style.backgroundColor = data["color"]
        start_button = $("#start_button");
        start_button.hide();

    })
    .fail(function(){

    })
    
})

$('#answer_button').on('click',function(){

  let picker_data = $('#picker').spectrum('get');
  let color = [Math.floor(picker_data['_r']),Math.floor(picker_data['_g']),Math.floor(picker_data['_b'])];
  let position = [$('#objX').val(), $('#objY').val(), $('#objW').val(), $('#objH').val()]

  let data = {
    uuid: captcha_uuid,
    color: color,
    position: position
  };
  
  $.ajax({
      url: 'http://localhost:8080/response',
      type: 'POST',
      data: JSON.stringify(data),
      dataType: 'json',
      contentType: 'application/json',
      timeout: 5000,
  })
  .done(function(data,textStatus,jqXHR){
    let result = parseInt(data.result,10);

    if(result <= 30 ){
      $('#captcha_result').text("正解");
      $('#captcha_result').css({
        "background-color" : "#8AC75A",
        "opacity": "70%"
        });
    }
    else{
      $('#captcha_result').text("誤り");
      $('#captcha_result').css({
        "background-color" : "#C73228",
        "opacity": "70%"
        });
    }
    $('#captcha_result').fadeIn(300, function() {
      $('#captcha_result').fadeOut(300);
      captcha_cnt++;
      $('#captcha_cnt').text(captcha_cnt);
      if(captcha_cnt >= experiment_num)
      {
        alert("CAPTCHA test is done!");
		$('#captcha').hide();
		$('#title').hide();
        return;
      }
      $('#start_button').trigger("click");
    })
  });
  /*
  .fail(function(){

  });
  */
});

function setForm(){
    $('#objX').val(Math.floor(objX));
    $('#objY').val(Math.floor(objY));
    $('#objW').val(Math.floor(objX + objW));
    $('#objH').val(Math.floor(objY + objH));
}

function onDown(e){
    let offsetX = canvas.getBoundingClientRect().left;
    let offsetY = canvas.getBoundingClientRect().top;
    x = e.clientX - offsetX;
    y = e.clientY - offsetY;

    if(x+objW/2 > canvas.width){
      x = canvas.width - objW/2;
    }
    else if(x-objW/2 < 0){
      x = objW/2 + 1;
    }

    if(y+objH/2 > canvas.height){
      y = canvas.height - objH/2;
    }
    else if(y-objH/2 < 0){
      y = objW/2 + 1;
    }

    if(x >= objX && x <= objX + objW && y >= objY && y <= objY+objH){
      dragging = true;
      relX = objX - x;
      relY = objY - y;
    }
    else{
      dragging = true;
      objX = x - 1- objW/2;
      objY = y - 1- objH/2;
      relX = objX - x;
      relY = objY - y;
      setForm();
    }
  }

  function onMove(e){
    let offsetX = canvas.getBoundingClientRect().left;
    let offsetY = canvas.getBoundingClientRect().top;
    x = e.clientX - offsetX;
    y = e.clientY - offsetY;

    if(x+objW/2 > canvas.width){
      x = canvas.width - objW/2;
    }
    else if(x-objW/2 < 0){
      x = objW/2 + 1;
    }
    if(dragging){
      objX = x + relX;
      objY = y + relY;
      setForm();
    }
  }

function onUp(e){
    dragging = false;
}
