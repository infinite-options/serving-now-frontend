function favMeal() {

    var request = new XMLHttpRequest();

    var fav_meal = document.getElementById("fav-meal-btn");

    var fav_meal_id = fav_meal.getAttribute("data-meal_id");

    request.open("POST", 'kitchen/meals/fav/' + fav_meal_id, /* async = */ true);
    request.send();
    console.log(request.response);
}