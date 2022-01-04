import os

from flask_login import UserMixin

from chess import db, login_manager, app


@login_manager.user_loader
def load_user(user_id: int):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    image = db.Column(db.String(200), nullable=False, default='default.jpeg')

    players = db.relationship('Player')

    def get_image_url(self):
        return os.path.join(app.config['UPLOAD_URL'], self.image)

    def __repr__(self):
        return f'User(username={self.username}, email={self.email}, image={self.image})'


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    game_length = db.Column(db.Interval, nullable=False)
    supplement = db.Column(db.Interval, nullable=False)
    fen = db.Column(db.String(100), nullable=False, default='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

    players = db.relationship('Player', backref='game')
    moves = db.relationship('Move', backref='game')

    def get_fen_pos(self):
        return self.fen.split()[0]

    def get_active_color(self):
        return self.fen.split()[1]

    def get_castling_availability(self):
        return self.fen.split()[2]

    def get_enpassand_target(self):
        return self.fen.split()[3]

    def get_halfmove_clock(self):
        return self.fen.split()[4]

    def get_fullmove_number(self):
        return self.fen.split()[5]

    def update_fen(self, new_fen_pos: str):
        color = "b" if self.get_active_color() == "w" else "w"
        self.fen = new_fen_pos + " " + color + " KQkq - 0 1"
        db.session.commit()

    def add_move(self, piece: str, source: str, target: str):
        if self.moves == []:
            index = 1
        else:
            index = self.moves[-1].index + 1

        move = Move(
            index=index,
            piece=piece,
            source=source,
            target=target
        )
        self.moves.append(move)

        db.session.commit()

    def __repr__(self):
        return f'Game(players={self.players}, start_time={self.start_time}, game_length={self.game_length}, moves={self.moves}, fen={self.fen})'


class Player(db.Model):
    """Helper model for game being able to have 2 players"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.ForeignKey('game.id'), nullable=False)
    color = db.Column(db.String(5), nullable=False)

    user = db.relationship('User')

    def __repr__(self):
        return f'Player(user={self.user.username}, game_id={self.game_id}, color={self.color})'


class Move(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.ForeignKey('game.id'), nullable=False)
    index = db.Column(db.Integer, nullable=False)
    source = db.Column(db.String(10))
    target = db.Column(db.String(10))
    piece = db.Column(db.String(1))

    def __repr__(self):
        return f'Move(game_id={self.game_id}, index={self.index}, piece={self.piece}, source={self.source}, target={self.target})'
