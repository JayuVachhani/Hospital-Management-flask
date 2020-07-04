
// register
function validationn() {
    var validate = true;

    document.getElementById("usernamespan").innerHTML = "";
    document.getElementById("passwordspan").innerHTML = "";
    var username = document.getElementById("username").value;

    if (!username.match("^[a-zA-Z][a-zA-Z0-9]+$")) {
        document.getElementById("usernamespan").innerHTML = "Username should be alphanumeric!"
        validate = false;
    }

    //Patient name
    var password = document.getElementById("password").value;
    console.log(password);
    // console.log(password.match("/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,15}$"))
    var re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}/


    // if (!password.match(regex)) {
    if (!re.test(password)) {
        document.getElementById("passwordspan").innerHTML = "Password must contain at least one lowercase,uppercase,digit and special character!";
        validate = false;
    }
    return validate;

}

// validation create patient
function patientvalidation() {
    var validate = true
    document.getElementById("ssnidspan").innerHTML = "";
    document.getElementById("pnamespan").innerHTML = "";
    var ssnid = document.getElementById("ssnid").value;


    if (ssnid.length != 9) {
        document.getElementById("ssnidspan").innerHTML = "Enter 9 digit SSNID, given input length is :" + ssnid.length;
        validate = false
    }

    //Patient name
    var pname = document.getElementById("pname").value
    // console.log("Pname : "+ pname)
    // console.log(pname.match("^[a-zA-Z]+.*[\s][a-zA-Z]+$"))
    if (!pname.match("^[a-zA-Z]+$")) {
        document.getElementById("pnamespan").innerHTML = "Enter appropriate Patient Name";
        validate = false
    }
    return validate

}

// update patient
function updatevalidation() {
    var validate = true
    
    document.getElementById("pnamespan").innerHTML = "";
    //Patient name
    var pname = document.getElementById("pname").value
    // console.log("Pname : "+ pname)
    // console.log(pname.match("^[a-zA-Z]+.*[\s][a-zA-Z]+$"))
    if (!pname.match("^[a-zA-Z]+$")) {
        document.getElementById("pnamespan").innerHTML = "Enter appropriate Patient Name";
        validate = false
    }
    return validate

}

//update quantity

function qualityvalidation() {
    var validate = true;
    document.getElementById("updatemedidspan").innerHTML = "";
    var updatemedid = document.getElementById("updatemedid").value;

    if (updatemedid.length != 9) {
        document.getElementById("updatemedidspan").innerHTML =
            "Enter 9 digit medID, given input length is :" + updatemedid.length;
        validate = false;
    }
    return validate;
}

// resupply
function addvalidation() {
    var validate = true;
    document.getElementById("addmedidspan").innerHTML = "";
    document.getElementById("addmednamespan").innerHTML = "";
    var addmedid = document.getElementById("addmedid").value;

    if (addmedid.length != 9) {
        document.getElementById("addmedidspan").innerHTML =
            "Enter 9 digit medID, given input length is :" + addmedid.length;
        validate = false;
    }

    //Patient name
    var addmedname = document.getElementById("addmedname").value;
    // console.log("addmedname : "+ addmedname)
    // console.log(addmedname.match("^[a-zA-Z]+.*[\s][a-zA-Z]+$"))
    if (!addmedname.match("^[a-zA-Z]+$")) {
        document.getElementById("addmednamespan").innerHTML =
            "Enter Alphabetical Medicine Name";
        validate = false;
    }
    return validate;
}

// issuemedicine
function issuevalidation() {
    var validate = true;
    document.getElementById("mednamespan").innerHTML = "";

    //Patient name
    var medname = document.getElementById("medname").value;
    // console.log("medname : "+ medname)
    // console.log(medname.match("^[a-zA-Z]+.*[\s][a-zA-Z]+$"))
    if (!medname.match("^[a-zA-Z]+$")) {
        document.getElementById("mednamespan").innerHTML =
            "Enter Alphabetical Medicine Name";
        validate = false;
    }
    return validate;
}