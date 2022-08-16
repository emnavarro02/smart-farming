    //Initialize Firebase
    const config = {
        apiKey: "AIzaSyBfA9oYJI7BlnQ3jiJXajWyIkX_ZCjcaN0",
        authDomain: "smartgarden-fe7b3.firebaseapp.com",
        databaseURL: "https://smartgarden-fe7b3.firebaseio.com",
        storageBucket: "smartgarden-fe7b3.appspot.com", 
    };

    firebase.initializeApp(config);

    const MAX_MOIS = 100;
    const MIN_MOIS = 0;
    const MAX_TEMP = 60;
    const MIN_TEMP = -20;
    const MESSAGE_STATUS_DEVICE_ON  = "ON";
    const MESSAGE_STATUS_DEVICE_OFF = "OFF";
    const MESSAGE_TURNING_ON        = "Turning on...";
    const MESSAGE_TURNING_OFF       = "Turning off...";
    
    /* Settings Variables*/
    const SLIDER_TEMP_MIN = document.getElementById("slider-temp-min");
    const SLIDER_TEMP_MAX = document.getElementById("slider-temp-max");
    const SLIDER_MOIST_MIN = document.getElementById("slider-moist-min");
    const SLIDER_MOIST_MAX = document.getElementById("slider-moist-max");
    
    var SLIDER_TEMP_MAX_CURRENT_VALUE = document.getElementById('slider-temp-max-current-value');
    var SLIDER_TEMP_MIN_CURRENT_VALUE = document.getElementById('slider-temp-min-current-value');
    var SLIDER_MOIST_MAX_CURRENT_VALUE = document.getElementById('slider-moist-max-current-value');
    var SLIDER_MOIST_MIN_CURRENT_VALUE = document.getElementById('slider-moist-min-current-value');


    const ON = 1;
    const OFF = 0;

    var global_data;
    var outputStatus;
    var outputStatus_aux;
    var irrigationStatusMessage;
    var fanStatusMessage;


(function readData() {
    const preObject = document.getElementById('object');
    var btnFanStatus = document.getElementById('btnFanStatus');
    var txtFanStatus = document.getElementById('fan-status');
    var btnIrrigationStatus = document.getElementById('btnIrrigationStatus');

     //btnLoadingFanToggle         = document.getElementById('loading-fan-toggle');
     //btnFanToggle                = document.getElementById('fan-toggle');
     btnLoadingIrrigationToggle  = document.getElementById('loading-irrigation-toggle');
     btnIrrigationToggle         = document.getElementById('irrigation-toggle');
     irrigationStatusMessage     = document.getElementById('irrigation-status-message');
     fanStatusMessage            = document.getElementById('fan-status-message');
   
    const dbRefObject = firebase.database().ref().child('BROKER-01').child('Threshold');
    const dbOutputObject = firebase.database().ref().child('BROKER-01').child('DevicesStatus').child("5C:CF:7F:30:10:CD").child("Outputs");
    const dbAlertsObject = firebase.database().ref().child('BROKER-01').child('DevicesStatus').child("5C:CF:7F:30:10:CD").child("Alerts");
    const dbCurrentValueObject = firebase.database().ref().child('BROKER-01').child('DevicesStatus').child("5C:CF:7F:30:10:CD").child("CurrentValues");
    const dbBrokerStatus = firebase.database().ref().child('BROKER-01').child('BrokerStatus')


    dbCurrentValueObject.on('value', val => {
        currentValue = JSON.parse(JSON.stringify(val.val(), null, 3));
        //document.getElementById('dashboard-temperature').innerText = currentValue.Temperature.Value
        document.getElementById('dashboard-temperature').innerHTML = currentValue.Temperature.Value + "<span style='font-size:.5em;vertical-align:super;'>&deg;C</span>"
        
        
        //document.getElementById('dashboard-moisture').innerText  = currentValue.Moisture.Value
        document.getElementById('dashboard-moisture').innerHTML  = currentValue.Moisture.Value + "<span style='font-size:.5em;vertical-align:super;'>&percnt;</span>"

    });

    dbBrokerStatus.on('value', brokerStatus => {
        currentValue = JSON.parse(JSON.stringify(brokerStatus.val(), null, 3));
        if (currentValue.ON){
            document.getElementById('broker-status-message').innerHTML = "On"
            document.getElementById("status-display").style.backgroundColor = "green";
        }
        else{
            document.getElementById('broker-status-message').innerHTML = "Off"
            document.getElementById("status-display").style.backgroundColor = "gray";
        }
        document.getElementById('broker-id').innerHTML = currentValue.BrokerID
    });

    dbRefObject.on('value', snap => {
        //preObject.innerText = JSON.stringify(snap.val(), null, 3); 
        var data = JSON.parse(JSON.stringify(snap.val(), null, 3));
        global_data = data;
        document.getElementById("tresh-temp-max").innerText = data.Temperature.High;
        document.getElementById("tresh-temp-min").innerText = data.Temperature.Low;
        document.getElementById("tresh-mois-max").innerText = data.Moisture.High;
        document.getElementById("tresh-mois-min").innerText = data.Moisture.Low;

        SLIDER_TEMP_MIN.value = data.Temperature.Low;
        SLIDER_TEMP_MAX.value = data.Temperature.High;
        SLIDER_TEMP_MIN_CURRENT_VALUE.innerText = data.Temperature.Low;
        SLIDER_TEMP_MAX_CURRENT_VALUE.innerText = data.Temperature.High;
    

        SLIDER_MOIST_MIN.value = data.Moisture.Low;
        SLIDER_MOIST_MAX.value = data.Moisture.High;
        SLIDER_MOIST_MIN_CURRENT_VALUE.innerText = data.Moisture.Low;
        SLIDER_MOIST_MAX_CURRENT_VALUE.innerText = data.Moisture.High;
        
    });
    
    dbOutputObject.on('value', output => {
        outputStatus = JSON.parse(JSON.stringify(output.val(), null, 3));
                if (outputStatus.Fan.Status == ON){
                    btnFanStatus.checked = true;
                    document.getElementById('fan-toggle').style.backgroundColor = "#2ecc71";
                    fanStatusMessage.innerText = MESSAGE_STATUS_DEVICE_ON;

                    document.getElementById('loading-fan-toggle').style.display = "none";
                    document.getElementById('fan-toggle').style.display = "inline-block";

                    IS_FAN_WAITING = false;

                }
                else{
                    document.getElementById('fan-toggle').style.backgroundColor = "slategray";
                    btnFanStatus.checked = false;
                    fanStatusMessage.innerText = MESSAGE_STATUS_DEVICE_OFF;

                    document.getElementById('loading-fan-toggle').style.display = "none";
                    document.getElementById('fan-toggle').style.display = "inline-block";

                    IS_FAN_WAITING = false;

                }
                if (outputStatus.Irrigation.Status == ON){
                    btnIrrigationToggle.style.backgroundColor = "#2ecc71";
                    btnIrrigationStatus.checked = true;
                    irrigationStatusMessage.innerText = MESSAGE_STATUS_DEVICE_ON;
                    document.getElementById('loading-irrigation-toggle').style.display = "none";
                    document.getElementById('irrigation-toggle').style.display = "inline-block";
                    IS_IRRIGATION_WAITING = false;

                }
                else{
                    btnIrrigationStatus.checked = false;
                    btnIrrigationToggle.style.backgroundColor = "slategray";
                    irrigationStatusMessage.innerText = MESSAGE_STATUS_DEVICE_OFF;
                    document.getElementById('loading-irrigation-toggle').style.display = "none";
                    document.getElementById('irrigation-toggle').style.display = "inline-block";
                    IS_IRRIGATION_WAITING = false;

                } 
            
            IS_ON_LOAD = false;
        
    });

    dbAlertsObject.on('value' , alert => {
        var alertStatus = JSON.parse(JSON.stringify(alert.val(), null, 3));

        if (alertStatus.Temperature == 1) {
            document.getElementById("temperature-display").style.backgroundColor = "red";
            document.getElementById("icon-temperature").innerHTML = "<i class='fas fa-exclamation-triangle'></i>";

        } else {
            document.getElementById("temperature-display").style.backgroundColor = "lightblue";
            document.getElementById("icon-moisture").innerHTML = "<i class='fas fa-temperature-low'></i>"
        }
        

        if (alertStatus.Moisture == 1) {
            document.getElementById("moisture-display").style.backgroundColor = "red";
            document.getElementById("icon-moisture").innerHTML = "<i class='fas fa-exclamation-triangle'></i>";
        } else {
            document.getElementById("moisture-display").style.backgroundColor = "lightblue";
            document.getElementById("icon-moisture").innerHTML = "<i class='fas fa-tint'></i>";
        }

    });

}());

function writeData(){
    const dbRefObject = firebase.database().ref().child('BROKER-01').child('Threshold');

    /**
     *  DATA VALIDATION
     *  The code below assures that the data entered by the user is valid BEFORE attempting 
     *  to update the database. 
     * 
     *  The data is considered to be valid if all of the following are true:
     *  (a). new_high_mois is a numeric value lower than MAX_MOIS
     *  (b). new_high_mois is a numeric value greater than MIN_MOIS
     *  (c). new_high_temp is a numeric value lower than MAX_TEMP
     *  (d). new_low_temp is a numeric value greater than MIN_TEMP
     * 
     * Alternatively, if the user enters no data, then the current values are used. This
     * allows the user to update only a subset of values.
     * 
     * An appropriate message informs the user of whether or not an error occurred that
     * prevented the data to be submitted to the database.
     * 
    */


    var new_high_mois = SLIDER_MOIST_MAX.value;
    var new_low_mois  = SLIDER_MOIST_MIN.value;
    var new_high_temp = SLIDER_TEMP_MAX.value;
    var new_low_temp  = SLIDER_TEMP_MIN.value;
    var error_text = "ERROR SAVING\nFix these and try again.\n";
    
    var IS_DATA_VALID = true;
    document.getElementById("error-message").style.color = "red";

    if (new_high_mois <= new_low_mois || new_low_mois >= new_high_mois ){
        error_text += "- [ERROR] The value of High Moisture (" + new_high_mois + 
        "%) must be higher than the Low Moisture (" + new_low_mois + "%).\n";
        IS_DATA_VALID = false;
    }
    if (new_high_temp <= new_low_temp || new_low_temp >= new_high_temp){
        error_text += "- [ERROR] The value of High Temperature (" + new_high_temp + 
        "°C) must be higher than the Low Temperature (" + new_low_temp + "°C).\n";
        IS_DATA_VALID = false;
    }

/*
    // (a)
    if (new_high_mois.trim() === "") {
       new_high_mois = global_data.Moisture.High;
    } else if (isNaN(new_high_mois) || new_high_mois > MAX_MOIS) {
        error_text += "\nNew maximum moisture value seems to be invalid. Please enter a numeric value not greater than " + MAX_MOIS + ".";
        IS_DATA_VALID = false;
    }

    // (b)
    if (new_low_mois.trim() === "") {
        new_low_mois = global_data.Moisture.Low;
    } else if (isNaN(new_low_mois) || new_low_mois < MIN_MOIS) {
        error_text += "\nNew minimum moisture value seems to be invalid. Please enter a numeric value not lower than " + MIN_MOIS + ".";
        IS_DATA_VALID = false;
    }
    
    // (c)
    if (new_high_temp.trim() === "") {
        new_high_temp = global_data.Temperature.High;
    } else if (isNaN(new_high_temp) || new_high_temp > MAX_TEMP) {
        error_text += "\nNew maximum temperature value seems to be invalid. Please enter a numeric value not greater than " + MAX_TEMP + ".";
        IS_DATA_VALID = false;
    }

    // (d)
    if (new_low_temp.trim() === "") {
        new_low_temp = global_data.Moisture.Low;
    } else if (isNaN(new_low_temp) || new_low_temp < MIN_TEMP) {
        error_text += "\nNew minimum temperature value seems to be invalid. Please enter a numeric value not lower than " + MIN_TEMP + ".";
        IS_DATA_VALID = false;
    }
*/
    // Only valid data is submitted to the database
    if (IS_DATA_VALID) {
        var updatedVal = {'Moisture' : {'High' :  parseInt(new_high_mois,10), 
                                    'Low' : parseInt(new_low_mois, 10)
                                   },
                         'Temperature' : {'High' : parseInt(new_high_temp),
                                       'Low' : parseInt(new_low_temp)
                                    }
                                };
        dbRefObject.set(updatedVal);
        document.getElementById("error-message").style.color = "blue";
        error_text = "Data was submitted successfully.";
    }
    document.getElementById("error-message").innerText = error_text;
}

function switchOutputOnOff(){

    const dbRefObject = firebase.database().ref().child('BROKER-01').child('DevicesStatus').child("5C:CF:7F:30:10:CD").child("Outputs").child("Fan");
    
    if (outputStatus.Fan.Status == ON) {
        var updateVal = {'UserAction' : OFF}

    }
    else{
        var updateVal = {'UserAction' : ON}
    }
    dbRefObject.update(updateVal);
}

function switchOutputOnOff(idElement){
    const dbRefObject = firebase.database().ref().child('BROKER-01').child('DevicesStatus').child("5C:CF:7F:30:10:CD").child("Outputs");


    

     

    switch (idElement){
        case "btnIrrigationStatus":
            
            if (outputStatus.Irrigation.UserAction == ON) {
                dbRefObject.child('Irrigation').child('UserAction').set(OFF);
                irrigationStatusMessage.innerText = MESSAGE_TURNING_OFF;
                suspend_system()
            }
            else{
                dbRefObject.child('Irrigation').child('UserAction').set(ON);
                irrigationStatusMessage.innerText = MESSAGE_TURNING_ON;
                suspend_system()
            }
            break;
        case "btnFanStatus":
           if (outputStatus.Fan.UserAction == ON) {
                dbRefObject.child('Fan').child('UserAction').set(OFF);
                fanStatusMessage.innerText = MESSAGE_TURNING_OFF;
                suspend_system()
            }
            else{
                dbRefObject.child('Fan').child('UserAction').set(ON);
                fanStatusMessage.innerText = MESSAGE_TURNING_ON;
                suspend_system()

            }
    }
    
}
function suspend_system() {
    document.getElementById('irrigation-toggle').style.display = "none";
    document.getElementById('loading-irrigation-toggle').style.display = "inline-block";
    document.getElementById('fan-toggle').style.display = "none";
    document.getElementById('loading-fan-toggle').style.display = "inline-block";
}

/* delete?  :o  */

/*var slider = document.getElementById("myRange");
var output = document.getElementById("demo");
slider.value = 70;

output.innerText = SLIDER_TEMP_MIN.value;

SLIDER_TEMP_MIN.oninput = function() {
  output.innerHTML = this.value;
}
*/

SLIDER_TEMP_MIN.oninput = function() {
    SLIDER_TEMP_MIN_CURRENT_VALUE.innerText = this.value;
}

SLIDER_TEMP_MAX.oninput = function() {
    SLIDER_TEMP_MAX_CURRENT_VALUE.innerText = this.value;
}

SLIDER_MOIST_MIN.oninput = function() {
    SLIDER_MOIST_MIN_CURRENT_VALUE.innerText = this.value;
}

SLIDER_MOIST_MAX.oninput = function() {
    SLIDER_MOIST_MAX_CURRENT_VALUE.innerText = this.value;
}