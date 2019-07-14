function favMeal(id) {

    var request = new XMLHttpRequest();

    var host = 'http://localhost:8080'

    console.log('favMeal function called');

    // request.open("GET", '/kitchen/meals/fav/' + fav_meal_id, /* async = */ true);
    
    request.open("PUT", host + '/api/v1/meals/fav/' + id, /* async = */ true);

    request.send();
    console.log(request.response);
}