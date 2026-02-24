from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()


class Pomodoro(db.Model):
    """Pomodoroセッションモデル"""
    __tablename__ = 'pomodoros'
    
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String(50), nullable=False)
    end_time = db.Column(db.String(50), nullable=True)
    duration_sec = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='running')
    type = db.Column(db.String(20), nullable=False, default='work')
    
    def __repr__(self):
        return f'<Pomodoro {self.id} {self.status}>'
    
    def to_dict(self):
        """辞書形式に変換（APIレスポンス用）"""
        return {
            'id': self.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration_sec': self.duration_sec,
            'status': self.status,
            'type': self.type,
        }
