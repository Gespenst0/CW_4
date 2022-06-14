from flask import request
from flask_restx import Resource, Namespace, fields, abort
from marshmallow import ValidationError

from project.container import auth_service, user_service
from project.dao.models import UserSchema
from project.exceptions import UserAlreadyExists, ItemNotFound, IncorrectPassword, InvalidToken

auth_ns = Namespace('auth', description='Authorization and authentication')
user_schema = UserSchema()

# Define api model for documentation
auth_model = auth_ns.model('Registration', {
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})

tokens_model = auth_ns.model('Tokens', {
    'access_token': fields.String(required=True),
    'refresh_token': fields.String(required=True)
})


@auth_ns.route('/register/')
class AuthView(Resource):
    @auth_ns.doc(description='User registration', body=auth_model)
    @auth_ns.response(201, 'User registered')
    @auth_ns.response(400, 'Bad Request')
    def post(self):
        # Get and check credentials passed
        credentials = {
            'email': request.json.get('email'),
            'password': request.json.get('password')
        }
        if None in credentials.values():
            abort(400, 'Wrong fields passed')

        # Register user
        try:
            data = user_schema.load(credentials)
            user = user_service.create(data)
            return "", 201, {"location": f"/user/{user.id}"}
        except ValidationError:
            abort(400, 'Not valid data passed')
        except UserAlreadyExists:
            abort(400, 'User already exists')


@auth_ns.route('/login/')
class AuthView(Resource):
    @auth_ns.doc(description='Get tokens', body=auth_model)
    @auth_ns.response(201, 'Tokens created', tokens_model)
    @auth_ns.response(400, 'Bad Request, not valid data passed')
    @auth_ns.response(401, 'Unauthorized, wrong password')
    @auth_ns.response(404, 'Not Found, no user with such e-mail')
    def post(self):
        # Get and check credentials passed
        credentials = {
            'email': request.json.get('email'),
            'password': request.json.get('password')
        }
        if None in credentials.values():
            abort(400, 'Not valid data passed')

        # Generate tokens
        try:
            tokens = auth_service.generate_tokens(credentials)
            return tokens, 201
        except ItemNotFound:
            abort(404, 'User not found')
        except IncorrectPassword:
            abort(401, 'Incorrect password')

    @auth_ns.doc(description='Get new tokens')
    @auth_ns.response(201, 'Tokens created', tokens_model)
    @auth_ns.response(401, 'Invalid refresh token')
    def put(self):
        try:
            # Check data validity
            refresh_token = request.json.get('refresh_token')
            if not refresh_token:
                abort(400, 'Not valid data passed')

            # Get tokens
            tokens = auth_service.approve_token(refresh_token)
            return tokens, 201

        except InvalidToken:
            abort(401, 'Invalid token passed')
