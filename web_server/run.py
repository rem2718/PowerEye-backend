#run.py:
from app import create_app
from config import app

if __name__ == '__main__':
    app = create_app(app.config['development'])
    app.run(debug=True)

