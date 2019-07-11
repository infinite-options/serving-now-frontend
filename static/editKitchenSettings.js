const BASE_URL = 'http://localhost:5000/api/v1';
const ENDPOINT = 'kitchen';

function updateRegistration(id) {
  var un = $('#username').val();
  var pw = $('#password').val();
  var vpw = $('#verify-password').val();

  if (pw !== vpw) return;

  var uri = `${BASE_URL}/${ENDPOINT}/${id}`;
  var body = {
      type: 'registration',
      payload: {
          username: un,
          password: pw
      }
  };

  $.ajax({
      url: uri,
      type: 'PUT',
      crossDomain: true,
      data: JSON.stringify(body),
      dataType: 'json',
      success: function(result) {
          console.log(result);
      }
  })
}

function updatePersonal(id) {
  var name = $('#name').val();
  var a = $('#street').val();
  var c = $('#city').val();
  var sta = $('#state').val();
  var zc = $('#zipCode').val();
  var pn = $('#phone_number').val();
  var e = $('#email').val();

  var names = name.split(' ');
  if (names.length !== 2) return;
  var fn = names[0];
  var ln = names[1];
 
  var uri = `${BASE_URL}/${ENDPOINT}/${id}`;
  var body = {
      type: 'personal',
      payload: {
          first_name: fn,
          last_name: ln,
          address: a,
          city: c,
          state: sta,
          zipcode: zc,
          phone_number: pn,
          email: e
      }
  };

  $.ajax({
      url: uri,
      type: 'PUT',
      crossDomain: true,
      data: JSON.stringify(body),
      dataType: 'json',
      success: function(result) {
          console.log(result);
      }
  })
}

function updateKitchen(id) {
  var n = $('#kitchen_name').val();
  var d = $('#description').val();
  var ot = $('#open_time').val();
  var ct = $('#close_time').val();
  var dev = $('#delivery').is(':checked') ? $('#delivery').val() : $('#pickup').val();
  var co = $('#reusuable').is(':checked') ? $('#reusable').val() : $('#disposable').val();
  var cao = $('#can_cancel').is(':checked') ? $('#can_cancel').val() : $('#cannot_cancel').val();

  var uri = `${BASE_URL}/${ENDPOINT}/${id}`;
  var body = {
      type: 'kitchen',
      payload: {
          name: n,
          description: d,
          open_time: ot,
          close_time: ct,
          delivery_option: dev,
          container_option: co,
          cancellation_option: cao
      }
  };
 
  $.ajax({
      url: uri,
      type: 'PUT',
      crossDomain: true,
      data: JSON.stringify(body),
      dataType: 'json',
      success: function(result) {
          console.log(result);
      }
  })
}
