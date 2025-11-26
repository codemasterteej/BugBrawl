"""
Application entry point
Run this file to start the server: python run.py
"""
from app import create_app, db

app = create_app()

# Create database tables
with app.app_context():
    db.create_all()
    print("Database initialized!")

if __name__ == '__main__':
    # host='0.0.0.0' makes it accessible from other devices on your network
    # debug=True enables auto-reload and better error messages
    app.run(host='0.0.0.0', port=6000, debug=True)
