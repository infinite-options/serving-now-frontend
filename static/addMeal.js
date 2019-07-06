
function postMeal() {
    console.log('post meal function called');
    var request = new XMLHttpRequest();
    var formData = new FormData();

    var meal_options_elem = document.getElementById('option-items');
    var meal_options = meal_options_elem.options[meal_options_elem.selectedIndex].value;

    var items= {};
    var options = [];

    for (var i = 1; i <= meal_options; i++){
        var name_id = 'add_meal_option'.concat(i, '_name');
        var qty_id = 'add_meal_option'.concat(i, '_qty');
        var item_name= document.getElementById(name_id).value;
        var item_qty_id = document.getElementById(qty_id);
        var item_qty = item_qty_id.options[item_qty_id.selectedIndex].value;
        var obj = {}
        obj["title"] = item_name
        obj["qty"] = item_qty
        options.push(obj);
    }

    items['meal_items'] = options
    console.log(items);

    // Bind the FormData object and the form element
    formData.append('name', document.getElementById('add_meal_mealname').value)
    formData.append('items', JSON.stringify(items))
    formData.append('price', document.getElementById('add_meal_price').value)
    formData.append('photo', document.getElementById('add_meal_image').files[0]);

    // Set up our request
    // request.open("POST", "https://o5yv1ecpk1.execute-api.us-west-2.amazonaws.com/dev/api/v1/meals/" + kitchen_id, true);
    //XHR.open("POST", "http://127.0.0.1:5000/api/v1/meals/" + "0001", true);

    // The data sent is what the user provided in the form
    request.open("POST", "/kitchens/meals/create", true);
    request.send(formData);
}