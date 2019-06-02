from flask import Flask, request, Response

from FlaskServer.flask_processing import *


app = Flask(__name__)


@app.route('/')
def index():
    return '''
    <center><h1>Welcome, user!</h1></center>
    <h3>Request type GET</h3>
    <li>/users - Показать всех пользователей</li>
    <li>/users?UserId=[id] - Информация о конкретном пользователе</li>
    <li>/subscriptions/categories?UserId=[type(int) id] - Получение подписок на категории</li>
    <h3>Request type POST</h3>
    <li>/users
    <p>{
        "vkUserId": [type(int) default: 0]
        "FirstName": "[type(text) First Name]",
        "LastName": "[type(text) Last Name]",
    }</p></li>
    <li>/subscriptions/categories
    <p>{
        "UserId": [type(int) default: 0]
        "category": "[type(text) First Name]",
    }</p></li>
    '''


@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        data = get_users(request.args)
        return Response(data['result'], status=data['code'], mimetype='application/json')
    elif request.method == 'POST':
        data = create_user(request.json)
        return Response(data['result'], status=data['code'], mimetype='application/json')


@app.route('/news')
def news():
    data = get_news(request.args)
    return Response(data['result'], status=data['code'], mimetype='application/json')


@app.route('/subscriptions/<name_type>', methods=['GET', 'POST', 'PUT'])
def subscriptions(name_type):
    if request.method == 'GET':
        params = request.args
        if name_type == 'categories':
            data = get_categories(params)
            return Response(data['result'], status=data['code'], mimetype='application/json')
        elif name_type == 'keywords':
            data = get_keywords(params)
            return Response(data['result'], status=data['code'], mimetype='application/json')

    elif request.method == 'POST':
        params = request.json
        if name_type == 'categories':
            data = create_categories(params)
            return Response(data['result'], status=data['code'], mimetype='application/json')
        elif name_type == 'keywords':
            data = create_keywords(params)
            return Response(data['result'], status=data['code'], mimetype='application/json')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
