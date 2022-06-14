from project.config import DevelopmentConfig
from project.server import create_app

app = create_app(DevelopmentConfig)

if __name__ == '__main__':
    app.run(port='25000')
