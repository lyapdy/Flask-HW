import datetime
from flask import Flask, jsonify, request
from flask.views import MethodView
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from jsonschema import validate, ValidationError
from schema import CREATE_USER, CREATE_ADVERTISEMENT, UPDATE_ADVERTISEMENT

PG_DSN = 'postgresql://user1:user1@127.0.0.1:5433/flask_hw4'
app = Flask('first_flask_app')
app.config.from_mapping(SQLALCHEMY_DATABASE_URI=PG_DSN)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class UserModel(db.Model):
    """Пользователь."""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), index=True, nullable=False, unique=True)
    advertisements = db.relationship('AdvertisementModel', backref='user', lazy=True)

class AdvertisementModel(db.Model):
    """Объявление."""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(64), index=True, nullable=False)
    description = db.Column(db.String(256), default='', index=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    owner = db.Column(db.Integer, db.ForeignKey("user_model.id"), nullable=True)

    def serialize(self):
        """Return in JSON-serializable format"""
        return {
            'id': self.id,
            'title': self.title
        }



class UserView(MethodView):
    def get(self, user_id):
        user = UserModel.query.get(user_id)
        if user is not None:
            return jsonify({
                'id': user.id,
                'name': user.name,
                'advertisements': [ad.serialize() for ad in user.advertisements]
            })
        else:
            response = jsonify({'error': 'not found'})
            response.status_code = 404
            return response
    def post(self):
        try:
            validate(request.json, CREATE_USER)
        except ValidationError as er:
            response = jsonify({
                'error': 'not valid',
                'description': er.message
            })
            response.status_code = 400
            return response
        user_name = request.json.get('name')
        if not UserModel.query.filter_by(name=user_name).first():
            new_user = UserModel(name=user_name)
            db.session.add(new_user)
            db.session.commit()
            return jsonify({
                'id': new_user.id,
                'name': new_user.name
            })
        else:
            response = jsonify({'error': 'This user already exists'})
            response.status_code = 400
            return response
    def delete(self, user_id):
        user = db.session.query(UserModel).filter(UserModel.id == user_id).first()
        if user is not None:
            try:
                db.session.delete(user)
                db.session.commit()
                return jsonify({'status': 'deleted'})
            except:
                response = jsonify({'error': 'SQL error'})
                response.status_code = 500
                return response
        else:
            response = jsonify({'error': 'This user does not exist'})
            response.status_code = 404
            return response

class AdvertisementView(MethodView):
    def get(self, ad_id):
        ad = AdvertisementModel.query.get(ad_id)
        if ad is not None:
            return jsonify({
                'id': ad.id,
                'title': ad.title,
                'description': ad.description,
                'created_at': ad.created_at,
                'updated_at': ad.updated_at,
                'owner': ad.owner,
            })
        else:
            response = jsonify({'error': 'not found'})
            response.status_code = 404
            return response
    def post(self):
        try:
            validate(request.json, CREATE_ADVERTISEMENT)
        except ValidationError as er:
            response = jsonify({
                'error': 'not valid',
                'description': er.message
            })
            response.status_code = 400
            return response
        ad_owner = request.json.get('owner')
        if UserModel.query.filter_by(id=ad_owner).first():
            ad_title = request.json.get('title')
            ad_description = request.json.get('description')
            new_ad = AdvertisementModel(
                title=ad_title,
                description=ad_description,
                owner=ad_owner
            )
            db.session.add(new_ad)
            db.session.commit()
            return jsonify({
                'id': new_ad.id,
                'title': new_ad.title,
                'description': new_ad.description,
                'created_at': new_ad.created_at,
                'owner': new_ad.owner,
            })
        else:
            response = jsonify({'error': 'This user does not exist'})
            response.status_code = 404
            return response
    def put(self, ad_id):
        ad = AdvertisementModel.query.get(ad_id)
        if ad is not None:
            try:
                validate(request.json, UPDATE_ADVERTISEMENT)
            except ValidationError as er:
                response = jsonify({
                    'error': 'not valid',
                    'description': er.message
                })
                response.status_code = 400
                return response
            ad_owner = request.json.get('owner')
            if ad_owner:
                if UserModel.query.filter_by(id=ad_owner).first():
                    ad.owner = ad_owner
                else:
                    response = jsonify({'error': 'This owner does not exist'})
                    response.status_code = 404
                    return response
            if request.json.get('title'):
                ad.title = request.json.get('title')
            if request.json.get('description'):
                ad.description = request.json.get('description')
            db.session.commit()
            return jsonify({
                'id': ad.id,
                'title': ad.title,
                'description': ad.description,
                'created_at': ad.created_at,
                'updated_at': ad.updated_at,
                'owner': ad.owner
            })

        else:
            response = jsonify({'error': 'This advertisement does not exist'})
            response.status_code = 404
            return response
    def delete(self, ad_id):
        ad = db.session.query(AdvertisementModel).filter(AdvertisementModel.id == ad_id).first()
        if ad is not None:
            try:
                db.session.delete(ad)
                db.session.commit()
                return jsonify({'status': 'deleted'})
            except:
                response = jsonify({'error': 'SQL error'})
                response.status_code = 500
                return response
        else:
            response = jsonify({'error': 'not found'})
            response.status_code = 404
            return response




app.add_url_rule('/api/user', view_func=UserView.as_view('user_create'), methods=['POST'])
app.add_url_rule('/api/user/<int:user_id>', view_func=UserView.as_view('user_get'), methods=['GET'])
app.add_url_rule('/api/user/<int:user_id>', view_func=UserView.as_view('user_delete'), methods=['DELETE'])

app.add_url_rule('/api/ad', view_func=AdvertisementView.as_view('ad_create'), methods=['POST'])
app.add_url_rule('/api/ad/<int:ad_id>', view_func=AdvertisementView.as_view('ad_get'), methods=['GET'])
app.add_url_rule('/api/ad/<int:ad_id>', view_func=AdvertisementView.as_view('ad_delete'), methods=['DELETE'])
app.add_url_rule('/api/ad/<int:ad_id>', view_func=AdvertisementView.as_view('ad_update'), methods=['PUT'])

app.run(host='0.0.0.0', port=8080)