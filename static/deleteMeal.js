function deleteMeal(id) {
    var request = new XMLHttpRequest();

    request.open("GET", '/api/v1/meals/' + id, /* async = */ true);
    request.send();
}