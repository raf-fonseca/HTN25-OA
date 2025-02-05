from app import create_app
from app.database.schema import init_db

app = create_app()
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

