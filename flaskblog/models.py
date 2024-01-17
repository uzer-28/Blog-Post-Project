from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flaskblog import db, login_manager, app
from flask_login import UserMixin                           #usermixin is used for authentication purpose

@login_manager.user_loader                                  #this user_loader loads the user info with specified user_id
def load_user(user_id):                                     #and store the return value in the 'current_user'
    return User.query.get(int(user_id))
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(35), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    image_file = db.Column(db.String(60), nullable=False, default='default.jpg')
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(me, expires_sec=1800):                    #generates a time-limited token that includes information about a user
        s = Serializer(app.config['SECRET_KEY'], expires_sec)     #The generated token can be sent to the user via a secure channel (e.g., email) as part of a password reset link.
        return  s.dumps({'user_id':me.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):                               #responsible for verifying the validity of a reset token.
        s = Serializer(app.config['SECRET_KEY'])                 #takes a token as input and attempts to decode it using the same secret key used during token generation.
        try:                                                     #If the decoding is successful, it extracts the user ID from the token's payload.
            user_id = s.loads(token)['user_id']                  #It then attempts to retrieve the user with the corresponding user ID from the database.
        except:                                                  #If the user is found, the assumption is that the token is valid, and the associated user is returned. If the token is invalid or expired, None is returned.
            return None
        return User.query.get(user_id)

    def __repr__(me) -> str:
        return f"User('{me.username}', '{me.email}', '{me.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(me) -> str:
        return f"Post('{me.title}', '{me.date_posted}')"