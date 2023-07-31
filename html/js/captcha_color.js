let canvas, ctx;
let objX, objY, objW, objH;
let dragging = false;
let captcha_uuid;

let interval_id = 0;
let experiment_num = 10;
let captcha_cnt = 0;

$('#picker').spectrum({
    type: "flat",
  showPalette: false,
  hideAfterPaletteSelect: true,
  showInitial: true,
  showAlpha: false,
  showButtons: false,
  allowEmpty: false
});


// Startボタンをクリックすると以下が実行されます．
$('#start_button').on('click',function(){
    
    if(captcha_cnt >= experiment_num){
      alert("CAPTCHA test is done!");
      return;
    }

    $.ajax({
        url: 'http://127.0.0.1:8081/challenge',
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
        position = data["position"]
        x_ul = position[0]
        y_ul = position[1]
        x_lr = position[2]
        y_lr = position[3]

        objW = 5;
        objH = 5;
        objX = (x_ul+x_lr) / 2 - objW/2;
        objY = (y_ul+y_lr) / 2 - objH/2;
        var img = new Image();
        img.onload = function(){
            if(canvas.getContext){

                if(interval_id != 0)
                {
                  clearInterval(interval_id);
                }

                setForm();
                const drawRect = img => {
                    ctx.clearRect(0,0,canvas.width,canvas.height);
                    ctx.drawImage(img,0,0);
                    ctx.globalAlpha = 1; //透明度
                    ctx.strokeRect(objX,objY,objW,objH);
                    //ctx.strokeRect(x_ul, y_ul, x_lr-x_ul, y_lr-y_ul)
                }
                interval_id = setInterval(function(){drawRect(img)},50);
            }
        }
        img.src = "data:image/png;base64," + data["blob"];
		captcha_uuid = data["uuid"];
        start_button = $("#start_button");
        start_button.hide();
		console.log(captcha_uuid);

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

  $('#picker').spectrum("set", "#000");
  
  $.ajax({
      url: 'http://localhost:8081/response',
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