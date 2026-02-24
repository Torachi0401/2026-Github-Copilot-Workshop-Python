class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///pomodoro.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
