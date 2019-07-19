function favMeal(id) {

    var request = new XMLHttpRequest();

    request.open("PUT", '/api/v1/meals/fav' + id, /* async = */ true);
    request.send();
}