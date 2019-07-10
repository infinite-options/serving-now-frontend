function deleteMeal() {
    console.log('deleteMeal function called');
    var request = new XMLHttpRequest();
    //var formData = new FormData();

    var delete_meal = document.getElementById("delete-meal-btn");

    var delete_meal_id = delete_meal.getAttribute("data-meal_id");

    //formData.append('meal_id', delete_meal_id);
    //console.log(formData);

    request.open("POST", 'kitchen/meals/delete' + delete_meal_id, /* async = */ true);
    request.send();
    console.log(request.response);
}