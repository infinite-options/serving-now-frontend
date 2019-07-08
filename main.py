# -*- coding: utf-8 -*-
# @Author: Japan Parikh
# @Date:   2019-05-24 19:40:12
# @Last Modified by:   Ranjit Marathay
# @Last Modified time: 2019-07-04 11:38:00

import boto3
import json
import uuid
import requests

from datetime import datetime
from pytz import timezone

from flask import Flask, Blueprint, request, render_template, redirect, url_for, flash
from flask import session as login_session
from flask_login import LoginManager, login_required, current_user, UserMixin, login_user, logout_user
from flask_mail import Mail, Message
from flask_restful import Resource, Api


from werkzeug.exceptions import BadRequest, NotFound
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__, static_folder='static', template_folder='templates')

login_manager = LoginManager(app)

secret_key = 'app_secret_key'

app.config['SECRET_KEY'] = secret_key
app.config['MAIL_USERNAME'] = 'infiniteoptions.meals@gmail.com'
app.config['MAIL_PASSWORD'] = 'annApurna'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)
api = Api(app)

db = boto3.client('dynamodb')
s3 = boto3.client('s3')

# aws s3 bucket where the image is stored
BUCKET_NAME = 'ordermealapp'

API_BASE_URL = 'https://o5yv1ecpk1.execute-api.us-west-2.amazonaws.com/dev/'

# allowed extensions for uploading a profile photo file
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])



# =======HELPER FUNCTIONS FOR UPLOADING AN IMAGE=============

def upload_meal_img(file, bucket, key):
    if file and allowed_file(file.filename):
        filename = 'https://s3-us-west-2.amazonaws.com/' \
                   + str(bucket) + '/' + str(key)
        upload_file = s3.put_object(
                            Bucket=bucket,
                            Body=file,
                            Key=key,
                            ACL='public-read',
                            ContentType='image/jpeg'
                        )
        return filename
    return None

def allowed_file(filename):
    """Checks if the file is allowed to upload"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ===========================================================


class User(UserMixin):
    def __init__(self, id):
        self.id = id

    @staticmethod
    def get(user_id):
        return User(user_id)


@login_manager.user_loader
def _login_manager_load_user(user_id):
    return User.get(user_id)


@app.route('/')
def index():
    return render_template('landing.html')


@app.route('/accounts/logout')
@login_required
def logout():
    del login_session['user_id']
    del login_session['name']
    logout_user()
    return redirect(url_for('index'))


@app.route('/accounts', methods=['GET', 'POST'])
@app.route('/accounts/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in login_session:
        return redirect(url_for('kitchen', id=login_session['user_id']))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Enter an email and password')
            return render_template('login.html')

        try:
            user = db.query(TableName="kitchens",
                IndexName='email-index',
                Limit=1,
                KeyConditionExpression='email = :val',
                ExpressionAttributeValues={
                    ':val': {'S': email}
                }
            )

            if user.get('Count') == 0:
                flash('User not found.')
                return render_template('login.html')

            if not check_password_hash(user['Items'][0]['password']['S'], \
              password):
                flash('Password is incorrect.')
                return render_template('login.html')
            else:
                user_id = user['Items'][0]['kitchen_id']['S']
                login_session['name'] = user['Items'][0]['name']['S']
                login_session['user_id'] = user_id
                login_user(User(user_id))
                return redirect(url_for('kitchen', id=user_id))

        except:
            flash('Unable to connect to database.')
            return render_template('login.html')

    return render_template('login.html')



@app.route('/accounts/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        verifyPassword = request.form.get('verify-password')
        username = request.form.get('username')
        firstName = request.form.get('first_name')
        lastName = request.form.get('last_name')
        kitchenName = request.form.get('name')
        phoneNumber = request.form.get('phone_number')
        closeTime = request.form.get('close_time')
        openTime = request.form.get('open_time')
        zipcode = request.form.get('zipcode')
        state = request.form.get('state')
        city = request.form.get('city')
        street = request.form.get('address')
        description = request.form.get('description')

        if email == None or password == None or verifyPassword == None \
          or username == None or firstName == None or lastName == None \
          or kitchenName == None or phoneNumber == None or closeTime == None \
          or openTime == None or zipcode == None or state == None or city == None \
          or street == None or description == None:
            flash('Please fill in all the required fields')
            return render_template('register.html')
        
        if verifyPassword != password:
            flash('Your passwords don\'t match')
            return render_template('register.html')

        request_data = {'email': email, 'password': password, 
                        'username': username, 'first_name': firstName,
                        'last_name': lastName, 'name': kitchenName, 
                        'address': street, 'city': city, 'state': state,
                        'zipcode': zipcode, 'description': description,
                        'phone_number': phoneNumber, 'close_time': closeTime,
                        'open_time': openTime}

        apiURL = API_BASE_URL +'api/v1/kitchens/register'
        response = requests.post(apiURL, data=json.dumps(request_data))

        if response.json().get('message') == 'Request failed. Please try again later.':
            flash('Kitchen registered successfully.')
            return
        else:
            return redirect(url_for('kitchen', id=response.json().get('kitchen_id')))

    return render_template('register.html')


@app.route('/kitchens/<string:id>')
@login_required
def kitchen(id):
    # return render_template('kitchen.html')
    # if 'name' not in login_session:
    #     return redirect(url_for('index'))
    #
    apiURL = API_BASE_URL +'/api/v1/meals/' + current_user.get_id()
    # apiURL = API_BASE_URL + '/api/v1/meals/' + '5d114cb5c4f54c94a8bb4d955a576fca'
    response = requests.get(apiURL)

    todaysMenu = response.json().get('result')

    return render_template('kitchen.html',
                            name=login_session['name'],
                            id=login_session['user_id'],
                            todaysMeals=todaysMenu)


@app.route('/kitchens/meals/create', methods=['POST'])
@login_required
def postMeal():
    name = request.form.get('name')
    price = request.form.get('price')
    photo = request.files.get('photo')
    itemsData = request.form.get('items')
    
    if name == None or price == None or photo == None or itemsData == None:
        print('Meal details missing')
        return

    kitchen_id = current_user.get_id()

    meal_id = uuid.uuid4().hex
    created_at = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%dT%H:%M:%S")

    meal_items = json.loads(itemsData)

    items = []
    for i in meal_items['meal_items']:
        item = {}
        item['title'] = {}
        item['title']['S'] = i['title']
        item['qty'] = {}
        item['qty']['N'] = str(i['qty'])
        items.append(item)

    description = [{'M': i} for i in items]

    # try:
    photo_key = 'meals_imgs/{}_{}'.format(str(kitchen_id), str(meal_id))
    photo_path = upload_meal_img(photo, BUCKET_NAME, photo_key)

    if photo_path == None:
        raise BadRequest('Request failed. \
            Something went wrong uploading a photo.')

    add_meal = db.put_item(TableName='meals',
        Item={'meal_id': {'S': meal_id},
              'created_at': {'S': created_at},
              'kitchen_id': {'S': str(kitchen_id)},
              'meal_name': {'S': str(name)},
              'description': {'L': description},
              'price': {'S': str(price)},
              'photo': {'S': photo_path}
        }
    )

    kitchen = db.update_item(TableName='kitchens',
        Key={'kitchen_id': {'S': str(kitchen_id)}},
        UpdateExpression='SET isOpen = :val',
        ExpressionAttributeValues={
            ':val': {'BOOL': True}
        }
    )

    return redirect(url_for('kitchen', id=current_user.get_id()))
    # except:
    #     raise BadRequest('Request failed. Please try again later.')


@app.route('/kitchens/meals/<string:meal_id>', methods=['POST'])
@login_required
def editMeal(meal_id):
    # print("edit meal api called: Server Side")
    # print(meal_id)
    name = request.form.get('name')
    price = request.form.get('price')
    photo = request.files.get('photo')
    items_data = request.form.get('items')
    limit = request.form.get('limit')

    if name != None:
        update_meal = db.update_item(TableName='meals',
                                     Key={'meal_id': {'S': meal_id}},
                                     UpdateExpression='SET meal_name = :n',
                                     ExpressionAttributeValues={
                                         ':n': {'S': str(name)}
                                     }
                                     )

    if price != None:
        update_meal = db.update_item(TableName='meals',
                                     Key={'meal_id': {'S': meal_id}},
                                     UpdateExpression='SET price = :n',
                                     ExpressionAttributeValues={
                                         ':n': {'S': str(price)}
                                     }
                                     )

    if photo != None:
        photo_key = 'meals_imgs/{}_{}'.format(str(current_user.get_id()), str(meal_id))
        photo_path = upload_meal_img(photo, BUCKET_NAME, photo_key)

        update_meal = db.update_item(TableName='meals',
                                     Key={'meal_id': {'S': meal_id}},
                                     UpdateExpression='SET photo = :n',
                                     ExpressionAttributeValues={
                                         ':n': {'S': photo_path}
                                     }
                                     )

    if items_data != None:
        meal_items = json.loads(items_data)

        items = []
        for i in meal_items['meal_items']:
            item = {}
            item['title'] = {}
            item['title']['S'] = i['title']
            item['qty'] = {}
            item['qty']['N'] = str(i['qty'])
            items.append(item)

        description = [{'M': i} for i in items]

        update_meal = db.update_item(TableName='meals',
                                     Key={'meal_id': {'S': meal_id}},
                                     UpdateExpression='SET description = :n',
                                     ExpressionAttributeValues={
                                         ':n': {'L': description}
                                     }
                                     )
    #
    # # TODO: if the limit was removed, update meal to remove the given limit
    # if limit != None:
    #     update_meal = db.update_item(TableName='meals',
    #                                  Key={'meal_id': {'S': meal_id}},
    #                                  UpdateExpression='SET #l = :l',
    #                                  ExpressionAttributeNames={
    #                                      '#l': 'limit'
    #                                  },
    #                                  ExpressionAttributeValues={
    #                                      ':n': {'N': str(limit)}
    #                                  }
    #                                  )

     # return redirect(url_for('kitchen', id="5d114cb5c4f54c94a8bb4d955a576fca"))
    return redirect(url_for('kitchen', id=current_user.get_id()))


@app.route('/kitchens/report')
@login_required
def report():
    if 'name' not in login_session:
        return redirect(url_for('index'))

    todays_date = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%d")
    orders = db.scan(TableName='meal_orders',
        FilterExpression='kitchen_id = :value AND (contains(created_at, :x1))',
        ExpressionAttributeValues={
            ':value': {'S': current_user.get_id()},
            ':x1': {'S': todays_date}
        }
    )

    apiURL = API_BASE_URL +'/api/v1/meals/' + current_user.get_id()
    response = requests.get(apiURL)
    
    todaysMenu = response.json().get('result')
    mealsToCook = todaysMenu

    for item in mealsToCook:
        item['qty'] = 0

    for order in orders['Items']:
        for meals in order['order_items']['L']:
            for item in mealsToCook:
                if item['meal_id']['S'] == meals['M']['meal_id']['S']:
                    item['qty'] += int(meals['M']['qty']['N'])
            for item in todaysMenu:
                if item['meal_id']['S'] == meals['M']['meal_id']['S']:
                    meals['M']['meal_name'] = item['meal_name']

    print(orders['Items'])
    print(mealsToCook)

    return render_template('report.html', 
                            name=login_session['name'], 
                            id=login_session['user_id'],
                            mealsToCook=mealsToCook,
                            orders=orders['Items'])


def closeKitchen(kitchen_id):
    closeKitchen = db.update_item(TableName='kitchens',
        Key={'kitchen_id': {'S': kitchen_id}},
        UpdateExpression='SET isOpen = :val',
        ExpressionAttributeValues={
            ':val': {'BOOL': False}                                                       
        }
    )

@app.route('/kitchens/hours')
def updateKitchensStatus():
    if request.headers['X-Appengine-Cron'] == 'true':
        currentTime = datetime.now(tz=timezone('US/Pacific')).strftime('%H:%M')

        kitchens = db.scan(TableName='kitchens')
        for kitchen in kitchens['Items']:
            closeTime = kitchen['close_time']['S']
            if kitchen['isOpen']['BOOL'] == True:
                if currentTime.rsplit(':', 1)[0] == closeTime.rsplit(':', 1)[0]:
                    if int(currentTime.rsplit(':', 1)[1]) > int(closeTime.rsplit(':', 1)[1]):
                        closeKitchen(kitchen['kitchen_id']['S'])
                elif int(currentTime.rsplit(':', 1)[0]) > int(closeTime.rsplit(':', 1)[0]):
                    closeKitchen(kitchen['kitchen_id']['S'])
        return 'testing cron jobs'


def kitchenExists(kitchen_id):
    # scan to check if the kitchen name exists
    kitchen = db.scan(TableName='kitchens',
                      FilterExpression='kitchen_id = :val',
                      ExpressionAttributeValues={
                          ':val': {'S': kitchen_id}
                      }
                      )

    return not kitchen.get('Items') == []


class MealOrders(Resource):
    def post(self):
        """Collects the information of the order
           and stores it to the database.
        """
        response = {}
        data = request.get_json(force=True)
        created_at = datetime.now(tz=timezone('US/Pacific')).strftime(
            "%Y-%m-%dT%H:%M:%S")

        if data.get('email') == None \
                or data.get('name') == None \
                or data.get('street') == None \
                or data.get('zipCode') == None \
                or data.get('city') == None \
                or data.get('state') == None \
                or data.get('totalAmount') == None \
                or data.get('paid') == None \
                or data.get('paymentType') == None \
                or data.get('ordered_items') == None \
                or data.get('phone') == None \
                or data.get('kitchen_id') == None:
            raise BadRequest('Request failed. Please provide all \
                              required information.')

        kitchenFound = kitchenExists(data['kitchen_id'])

        # raise exception if the kitchen does not exists
        if not kitchenFound:
            raise BadRequest('kitchen does not exist')

        order_id = uuid.uuid4().hex
        totalAmount = data['totalAmount']

        order_details = []

        for i in data['ordered_items']:
            item = {}
            item['meal_id'] = {}
            item['meal_id']['S'] = i['meal_id']
            item['qty'] = {}
            item['qty']['N'] = str(i['qty'])
            order_details.append(item)

        order_items = [{"M": x} for x in order_details]

        try:
            add_order = db.put_item(TableName='meal_orders',
                                    Item={'order_id': {'S': order_id},
                                          'created_at': {'S': created_at},
                                          'email': {'S': data['email']},
                                          'name': {'S': data['name']},
                                          'street': {'S': data['street']},
                                          'zipCode': {
                                              'N': str(data['zipCode'])},
                                          'city': {'S': data['city']},
                                          'state': {'S': data['state']},
                                          'totalAmount': {
                                              'N': str(totalAmount)},
                                          'paid': {'BOOL': data['paid']},
                                          'paymentType': {
                                              'S': data['paymentType']},
                                          'order_items': {'L': order_items},
                                          'phone': {'S': str(data['phone'])},
                                          'kitchen_id': {
                                              'S': str(data['kitchen_id'])}
                                          }
                                    )

            kitchen = db.get_item(TableName='kitchens',
                                  Key={'kitchen_id': {'S': data['kitchen_id']}},
                                  ProjectionExpression='#kitchen_name, address, city, \
                    #address_state, phone_number, pickup_time',
                                  ExpressionAttributeNames={
                                      '#kitchen_name': 'name',
                                      '#address_state': 'state'
                                  }
                                  )

            msg = Message(subject='Order Confirmation',
                          sender=os.environ.get('EMAIL'),
                          html=render_template('emailTemplate.html',
                                               order_items=data[
                                                   'ordered_items'],
                                               kitchen=kitchen['Item'],
                                               totalAmount=totalAmount,
                                               name=data['name']),
                          recipients=[data['email']])

            mail.send(msg)

            response['message'] = 'Request successful'
            return response, 200
        except:
            raise BadRequest('Request failed. Please try again later.')

    def get(self):
        """RETURNS ALL ORDERS PLACED TODAY"""
        response = {}
        todays_date = datetime.now(tz=timezone('US/Pacific')).strftime(
            "%Y-%m-%d")

        try:
            orders = db.scan(TableName='meal_orders',
                             FilterExpression='(contains(created_at, :x1))',
                             ExpressionAttributeValues={
                                 ':x1': {'S': todays_date}
                             }
                             )

            response['result'] = orders['Items']
            response['message'] = 'Request successful'
            return response, 200
        except:
            raise BadRequest('Request failed. please try again later.')


class RegisterKitchen(Resource):
    def post(self):
        response = {}
        data = request.get_json(force=True)
        created_at = datetime.now(tz=timezone('US/Pacific')).strftime(
            "%Y-%m-%dT%H:%M:%S")

        if data.get('name') == None \
                or data.get('description') == None \
                or data.get('email') == None \
                or data.get('username') == None \
                or data.get('password') == None \
                or data.get('first_name') == None \
                or data.get('last_name') == None \
                or data.get('address') == None \
                or data.get('city') == None \
                or data.get('state') == None \
                or data.get('zipcode') == None \
                or data.get('phone_number') == None \
                or data.get('close_time') == None \
                or data.get('open_time') == None:
            raise BadRequest('Request failed. Please provide all \
                              required information.')

        # scan to check if the kitchen name exists
        kitchen = db.scan(TableName="kitchens",
                          FilterExpression='#name = :val',
                          ExpressionAttributeNames={
                              '#name': 'name'
                          },
                          ExpressionAttributeValues={
                              ':val': {'S': data['name']}
                          }
                          )

        # raise exception if the kitchen name already exists
        if kitchen.get('Items') != []:
            response['message'] = 'This kitchen name is already taken.'
            return response, 400

        kitchen_id = uuid.uuid4().hex

        try:
            add_kitchen = db.put_item(TableName='kitchens',
                                      Item={'kitchen_id': {'S': kitchen_id},
                                            'created_at': {'S': created_at},
                                            'name': {'S': data['name']},
                                            'description': {
                                                'S': data['description']},
                                            'username': {'S': data['username']},
                                            'password': {
                                                'S': generate_password_hash(
                                                    data['password'])},
                                            'first_name': {
                                                'S': data['first_name']},
                                            'last_name': {
                                                'S': data['last_name']},
                                            'address': {'S': data['address']},
                                            'city': {'S': data['city']},
                                            'state': {'S': data['state']},
                                            'zipcode': {
                                                'N': str(data['zipcode'])},
                                            'phone_number': {
                                                'S': str(data['phone_number'])},
                                            'open_time': {
                                                'S': str(data['open_time'])},
                                            'close_time': {
                                                'S': str(data['close_time'])},
                                            'isOpen': {'BOOL': False},
                                            'email': {'S': data['email']}
                                            }
                                      )

            response['message'] = 'Request successful'
            response['kitchen_id'] = kitchen_id
            return response, 200
        except:
            raise BadRequest('Request failed. Please try again later.')


def formateTime(time):
    hours = time.rsplit(':', 1)[0]
    mins = time.rsplit(':', 1)[1]
    if hours == '00':
        return '{}:{} AM'.format('12', mins)
    elif hours >= '12' and hours < '24':
        if hours == '12':
            return '{}:{} PM'.format(hours, mins)
        return '{}:{} PM'.format((int(hours) - 12), mins)
    else:
        return '{}:{} AM'.format(hours, mins)

# Below here is all from app.py

class Kitchens(Resource):
    def get(self):
        """Returns all kitchens"""
        response = {}

        try:
            kitchens = db.scan(TableName='kitchens',
                               ProjectionExpression='#kitchen_name, kitchen_id, \
                    close_time, description, open_time, isOpen',
                               ExpressionAttributeNames={
                                   '#kitchen_name': 'name'
                               }
                               )

            result = []

            for kitchen in kitchens['Items']:
                kitchen['open_time']['S'] = formateTime(
                    kitchen['open_time']['S'])
                kitchen['close_time']['S'] = formateTime(
                    kitchen['close_time']['S'])

                if kitchen['isOpen']['BOOL'] == True:
                    result.insert(0, kitchen)
                else:
                    result.append(kitchen)

            response['message'] = 'Request successful'
            response['result'] = result
            return response, 200
        except:
            raise BadRequest('Request failed. Please try again later.')


class Meals(Resource):
    def post(self, kitchen_id):
        response = {}

        kitchenFound = kitchenExists(kitchen_id)

        # raise exception if the kitchen does not exists
        if not kitchenFound:
            raise BadRequest('kitchen does not exist')

        if request.form.get('name') == None \
                or request.form.get('items') == None \
                or request.form.get('price') == None:
            raise BadRequest('Request failed. Please provide required details.')

        meal_id = uuid.uuid4().hex
        created_at = datetime.now(tz=timezone('US/Pacific')).strftime(
            "%Y-%m-%dT%H:%M:%S")

        meal_items = json.loads(request.form['items'])

        items = []
        for i in meal_items['meal_items']:
            item = {}
            item['title'] = {}
            item['title']['S'] = i['title']
            item['qty'] = {}
            item['qty']['N'] = str(i['qty'])
            items.append(item)

        description = [{'M': i} for i in items]

        try:
            photo_key = 'meals_imgs/{}_{}'.format(str(kitchen_id), str(meal_id))
            photo_path = helper_upload_meal_img(request.files['photo'],
                                                BUCKET_NAME, photo_key)

            if photo_path == None:
                raise BadRequest('Request failed. \
                    Something went wrong uploading a photo.')

            add_meal = db.put_item(TableName='meals',
                                   Item={'meal_id': {'S': meal_id},
                                         'created_at': {'S': created_at},
                                         'kitchen_id': {'S': str(kitchen_id)},
                                         'meal_name': {
                                             'S': str(request.form['name'])},
                                         'description': {'L': description},
                                         'price': {
                                             'S': str(request.form['price'])},
                                         'photo': {'S': photo_path}
                                         }
                                   )

            kitchen = db.update_item(TableName='kitchens',
                                     Key={'kitchen_id': {'S': str(kitchen_id)}},
                                     UpdateExpression='SET isOpen = :val',
                                     ExpressionAttributeValues={
                                         ':val': {'BOOL': True}
                                     }
                                     )

            response['message'] = 'Request successful'
            return response, 201
        except:
            raise BadRequest('Request failed. Please try again later.')

    def get(self, kitchen_id):
        response = {}

        kitchenFound = kitchenExists(kitchen_id)

        # raise exception if the kitchen does not exists
        if not kitchenFound:
            raise BadRequest('kitchen does not exist')

        todays_date = datetime.now(tz=timezone('US/Pacific')).strftime(
            "%Y-%m-%d")

        try:
            meals = db.scan(TableName='meals',
                            FilterExpression='kitchen_id = :value and (contains(created_at, :x1))',
                            ExpressionAttributeValues={
                                ':value': {'S': kitchen_id},
                                ':x1': {'S': todays_date}
                            }
                            )

            for meal in meals['Items']:
                description = ''

                for item in meal['description']['L']:
                    if int(item['M']['qty']['N']) > 1:
                        description = description + item['M']['qty']['N'] + ' ' \
                                      + item['M']['title']['S'] + ', '
                    else:
                        description = description + item['M']['title'][
                            'S'] + ', '

                del meal['description']
                meal['description'] = {}
                meal['description']['S'] = description

            response['message'] = 'Request successful!'
            response['result'] = meals['Items']
            return response, 200
        except:
            raise BadRequest('Request failed. Please try again later.')


class OrderReport(Resource):
    def get(self, kitchen_id):
        response = {}

        kitchenFound = kitchenExists(kitchen_id)

        # raise exception if the kitchen does not exists
        if not kitchenFound:
            raise BadRequest('kitchen does not exist')

        todays_date = datetime.now(tz=timezone('US/Pacific')).strftime(
            "%Y-%m-%d")
        k_id = kitchen_id

        try:
            orders = db.scan(TableName='meal_orders',
                             FilterExpression='kitchen_id = :value AND (contains(created_at, :x1))',
                             ExpressionAttributeValues={
                                 ':value': {'S': k_id},
                                 ':x1': {'S': todays_date}
                             }
                             )

            response['result'] = orders['Items']
            response['message'] = 'Request successful'
            return response, 200
        except:
            raise BadRequest('Request failed. please try again later.')


api.add_resource(MealOrders, '/api/v1/orders')
api.add_resource(RegisterKitchen, '/api/v1/kitchens/register')
api.add_resource(Meals, '/api/v1/meals/<string:kitchen_id>')
api.add_resource(OrderReport, '/api/v1/orders/report/<string:kitchen_id>')
api.add_resource(Kitchens, '/api/v1/kitchens')


if __name__ == '__main__':
    app.run(host='localhost', port='8080', debug=True)