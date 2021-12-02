
function sendJSON(nam) {
    var result = document.getElementById("par_result");
    var checkBoxVar
    var val = "on"
    var sender_type = "chk"
    
    if (nam == "mister") {
        checkBoxVar = document.getElementById("chk_mister");
    } else if (nam == "lights") {
        checkBoxVar = document.getElementById("chk_lights");
    }
    else if (nam == "home_light") {
        checkBoxVar = document.getElementById("chk_home_light");
    }
    else if (nam == "roof_lights_sun") {
        checkBoxVar = document.getElementById("chk_roof_lights_sun");
    }
    else if (nam == "roof_lights_moon") {
        checkBoxVar = document.getElementById("chk_roof_lights_moon");
    } 
    else if (nam == "fan") {
        checkBoxVar = document.getElementById("chk_fan");
    }
    else if (nam == "dimmer") {
        sender_type="slider"
        var slider = document.getElementById("myRange");
        val=slider.value;
    }
    else if (nam == "refresh") {
        sender_type="btn_image"
        
        val="refresh";
    }
    if(sender_type=="chk" )
    {
        if (checkBoxVar.checked == false) {
            val = "off";
        } else {
            val = "on"
        }
    }


   

    // Creating a XHR object 
    let xhr = new XMLHttpRequest();
    let url = "change_status";

    // open a connection 
    xhr.open("POST", url, true);

    // Set the request header i.e. which type of content you are sending 
    xhr.setRequestHeader("Content-Type", "application/json");

    // Create a state change callback 
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {

            // Print received data from server 
            result.innerHTML = this.responseText;

        }
    };

    // Converting JSON data to string 
    var data = JSON.stringify({
        "name": nam,
        "value": val
    });

    // Sending data with the request 
    xhr.send(data);
    if(sender_type=="chk" )
    {
        var img_lbl = "img_";
        img_lbl = img_lbl.concat(nam);
        img_path = "/static/images/icons/";
        img_path = img_path.concat(nam, "-", val, "-100.png");
        document.getElementById(img_lbl).src = img_path;
    }
}
