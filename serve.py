from waitress import serve
from app import app  # Import the Flask app instance

if __name__ == "__main__":
    serve(app, host='127.0.0.1', port=8080)

