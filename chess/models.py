from flask_login import UserMixin

from chess import db, login_manager


@login_manager.user_loader
def load_user(user_id: int):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    image = db.Column(db.String(200), nullable=False, default='default.jpg')

    def __repr__(self):
        return f'User(username={self.username}, email={self.email}, image={self.image})'


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    game_length = db.Column(db.Interval, nullable=False)
    supplement = db.Column(db.Integer, nullable=False)

    players = db.relationship('Player', backref='game')
    moves = db.relationship('Move', backref='game')

    def __repr__(self):
        return f'Game(players={self.players}, start_time={self.start_time}, game_length={self.game_length} moves={self.moves})'


class Player(db.Model):
    """Helper model for game being able to have 2 players"""
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.ForeignKey('game.id'), nullable=False)
    color = db.Column(db.String(5), nullable=False)

    def __repr__(self):
        return f'Player(player_id={self.player_id}, game_id={self.game_id})'


class Move(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.ForeignKey('game.id'), nullable=False)
    index = db.Column(db.Integer, nullable=False)
    coords = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'Move(game_id={self.game_id}, index={self.index}, coords={self.coords})'
