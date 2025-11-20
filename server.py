from http.server import SimpleHTTPRequestHandler, HTTPServer
import mysql.connector
import os
import json
from urllib.parse import urlparse

# --- KONFIGURACJA ŚRODOWISKA ---
PORT = 8080

# Konfiguracja MySQL
DB_HOST = "mysql-db" 
DB_USER = os.getenv("MYSQL_USER", "root") 
DB_PASS = os.getenv("MYSQL_ROOT_PASSWORD", "rootpassword")
DB_NAME = os.getenv("MYSQL_DATABASE", "mydb")

# --- FUNKCJE POMOCNICZE ---

def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=3306,
        connection_timeout=5
    )

def initialize_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Tworzenie tabeli, jeśli nie istnieje
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                email VARCHAR(255)
            )
        """)
        conn.commit()
        conn.close()
        print("Database initialized successfully.")
    except mysql.connector.Error as err:
        print(f"Database initialization failed: {err}")

# --- HANDLER KLASY HTTP ---

class UserHandler(SimpleHTTPRequestHandler):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(UserHandler, '_db_initialized'):
            initialize_db()
            UserHandler._db_initialized = True

    def _send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    # METODA DO_GET (Uproszczona)
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/db-status':
            self._check_db_status() 
            return
            
        if parsed_path.path == '/users':
            self._list_users()
            return

        # Domyślna obsługa
        self._send_json_response(200, {"message": "Use /users (GET/POST) or /db-status."})

    # METODA DO_POST
    def do_POST(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/users':
            self._create_user() 
            return

        self._send_json_response(404, {"error": "Not Found"})
    
    # Logika dla endpointu /db-status
    def _check_db_status(self):
        try:
            conn = get_db_connection()
            conn.close()
            self._send_json_response(200, {"status": "OK", "message": "Successfully connected to MySQL container."})
        except mysql.connector.Error as err:
            self._send_json_response(500, {"status": "ERROR", "message": f"Connection failed: {err.msg}"})

    # Logika dla endpointu GET /users (Pobieranie z MySQL)
    def _list_users(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, name, email FROM users")
            users = cursor.fetchall()
            conn.close()

            self._send_json_response(200, {"users": users})

        except mysql.connector.Error as err:
            self._send_json_response(500, {"error": f"Failed to retrieve users: {err.msg}"})
    
    # Logika dla endpointu POST /users
    def _create_user(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            name = data.get('name')
            email = data.get('email')
            
            if not name or not email:
                self._send_json_response(400, {"error": "Name and email are required."})
                return

            conn = get_db_connection()
            cursor = conn.cursor()
            sql = "INSERT INTO users (name, email) VALUES (%s, %s)"
            cursor.execute(sql, (name, email))
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            
            self._send_json_response(201, {"id": new_id, "message": "User created successfully."})

        except Exception as e:
            self._send_json_response(500, {"error": f"Internal server error: {e}"})


if __name__ == "__main__":
    httpd = HTTPServer(("", PORT), UserHandler)
    print(f"Serving simplified CRUD app on port {PORT}. DB Host: {DB_HOST}")
    httpd.serve_forever()
