function favMeal(id) {

    var request = new XMLHttpRequest();

    request.open("PUT", '/api/v1/meals/' + id, /* async = */ true);
    request.send();
}