/*
* @Author: Japan Parikh
* @Date:   2019-05-24 21:51:33
* @Last Modified by:   Japan Parikh
* @Last Modified time: 2019-05-25 13:38:29
*/


function registerKitchen() {
	var formData = new FormData();
	var request = new XMLHttpRequest();

	var name = document.getElementById("name").value;
	var description = document.getElementById("description").value;
	var username = document.getElementById("username").value;
	var password = document.getElementById("password").value;
	var verifyPassword = document.getElementById("verify-password").value;
	var firstName = document.getElementById("first_name").value;
	var lastName = document.getElementById("last_name").value;
	var address = document.getElementById("street").value;
	var state = document.getElementById("state").value;
	var city = document.getElementById("city").value;
	var zipCode = document.getElementById("zipCode").value;
	var phoneNumber = document.getElementById("phone_number").value;
	var closeTime = document.getElementById("close_time").value;
	var openTime = document.getElementById("open_time").value;
	var email = document.getElementById("email").value;

	// if (name == "" || username == "" || password == "" || 
	// 	verifyPassword == "" || firstName == "" || lastName == "" || 
	// 	address == "" || city == "" || state == "" || 
	// 	phoneNumber == "" || zipcode == "" || closeTime == "" || 
	// 	openTime == "" || email == "") {

	// 	console.log("fields are empty");

	// } else {
	if (description != "") {
		formData.append("description", description);
	}

	formData.append("name", name);
	formData.append("username", username);
	formData.append("password", password);
	formData.append("verify-password", verifyPassword);
	formData.append("first_name", firstName);
	formData.append("last_name", lastName);
	formData.append("address", address);
	formData.append("state", state);
	formData.append("city", city);
	formData.append("zipcode", zipCode);
	formData.append("phone_number", phoneNumber);
	formData.append("close_time", closeTime);
	formData.append("open_time", openTime);
	formData.append("email", email);

	request.open("POST", "/accounts/register", true);
	request.send(formData);
	// }
}