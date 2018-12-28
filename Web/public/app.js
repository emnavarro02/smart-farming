    //Initialize Firebase
    const config = {
        apiKey: "AIzaSyBfA9oYJI7BlnQ3jiJXajWyIkX_ZCjcaN0",
        authDomain: "smartgarden-fe7b3.firebaseapp.com",
        databaseURL: "https://smartgarden-fe7b3.firebaseio.com",
        storageBucket: "smartgarden-fe7b3.appspot.com", 
    };

    firebase.initializeApp(config);

    const MAX_MOIS = 35;
    const MIN_MOIS = 10;
    const MAX_TEMP = 60;
    const MIN_TEMP = -20;

    const ON = 1;
    const OFF = 0;

    var global_data;
    var outputStatus;

(function readData() {
    const preObject = document.getElementById('object');
    var btnFanStatus = document.getElementById('btnFanStatus');
    var btnIrrigationStatus = document.getElementById('btnIrrigationStatus');
    
    const dbRefObject = firebase.database().ref().child('BROKER-01').child('Threshold');
    const dbOutputObject = firebase.database().ref().child('BROKER-01').child('DevicesStatus').child("5C:CF:7F:30:10:CD").child("Outputs");
    const dbAlertsObject = firebase.database().ref().child('BROKER-01').child('DevicesStatus').child("5C:CF:7F:30:10:CD").child("Alerts");
    
    dbRefObject.on('value', snap => {
        preObject.innerText = JSON.stringify(snap.val(), null, 3); 
        var data = JSON.parse(JSON.stringify(snap.val(), null, 3));
        global_data = data;
        document.getElementById("tresh-temp-max").placeholder = data.Temperature.High   + " (Max " + MAX_TEMP + ")";
        document.getElementById("tresh-temp-min").placeholder = data.Temperature.Low    + " (Min " + MIN_TEMP + ")";
        document.getElementById("tresh-mois-max").placeholder = data.Moisture.High      + " (Max " + MAX_MOIS + ")";
        document.getElementById("tresh-mois-min").placeholder = data.Moisture.Low       + " (Min " + MIN_MOIS + ")";
    });
    
    dbOutputObject.on('value', output => {
        outputStatus = JSON.parse(JSON.stringify(output.val(), null, 3));
        if (outputStatus.Fan.UserAction == ON){
            btnFanStatus.value = "Turn Off";
        }
        else{
            btnFanStatus.value = "Turn On";
        }

        if (outputStatus.Irrigation.UserAction == ON){
            btnIrrigationStatus.value = "Turn Off";
        }
        else{
            btnIrrigationStatus.value = "Turn On";
        }
    });

    dbAlertsObject.on('value' , alert => {
        var alertStatus = JSON.parse(JSON.stringify(alert.val(), null, 3));
        document.getElementById("alert-temperature").innerText = alertStatus.Temperature;
        document.getElementById("alert-moisture").innerText = alertStatus.Moisture;
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
     *                                   - by Daniel Navarro (https://www.danielnavarro.me)
     * 
    */
    var new_high_mois = document.getElementById("tresh-mois-max").value;
    var new_low_mois  = document.getElementById("tresh-mois-min").value;
    var new_high_temp = document.getElementById("tresh-temp-max").value;
    var new_low_temp  = document.getElementById("tresh-temp-min").value;
    var error_text = "Ooops... Something went wrong. Please fix the following errors:\n";
    var IS_DATA_VALID = true;
    document.getElementById("error-message").style.color = "red";
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

    // Only valid data is submitted to the database
    if (IS_DATA_VALID) {
        var updatedVal = {'Moisture' : {'High' :  new_high_mois, 
                                    'Low' : new_low_mois
                                   },
                         'Temperature' : {'High' : new_high_temp,
                                       'Low' : new_low_temp
                                    }
                                };
        dbRefObject.set(updatedVal);
        document.getElementById("error-message").style.color = "blue";
        error_text = "Great! The data was submitted successfully. You are awesome, you know it? :)";
    }
    document.getElementById("error-message").innerText = error_text;
}

function switchOutputOnOff(){

    const dbRefObject = firebase.database().ref().child('BROKER-01').child('DevicesStatus').child("5C:CF:7F:30:10:CD").child("Outputs").child("Fan");
    
    if (outputStatus.Fan.UserAction == ON) {
        var updateVal = {'UserAction' : OFF}
    }
    else{
        var updateVal = {'UserAction' : ON}
    }
    dbRefObject.update(updateVal);
}

function switchOutputOnOff(idElement){

    const dbRefObject = firebase.database().ref().child('BROKER-01').child('DevicesStatus').child("5C:CF:7F:30:10:CD").child("Outputs");
    var updateVal; 
    switch (idElement){
        case "btnIrrigationStatus":
            if (outputStatus.Irrigation.UserAction == ON) {
                dbRefObject.child('Irrigation').child('UserAction').set(OFF);
            }
            else{
                dbRefObject.child('Irrigation').child('UserAction').set(ON);
            }
            break;
        case "btnFanStatus":
            if (outputStatus.Fan.UserAction == ON) {
                dbRefObject.child('Fan').child('UserAction').set(OFF);
            }
            else{
                dbRefObject.child('Fan').child('UserAction').set(ON);
            }
        }

    //dbRefObject.update(updateVal);
}
