function deleteMeal(id) {
    console.log('deleteMeal function called');
    var request = new XMLHttpRequest();

    var delete_meal = document.getElementById("delete-meal-btn");

    var delete_meal_id = delete_meal.getAttribute("data-meal_id");

    request.open("GET", '/api/v1/meals/' + id, /* async = */ true);
    request.send();
    console.log(request.response);
}