from http.server import BaseHTTPRequestHandler, HTTPServer
import mysql.connector
import os
import json
from urllib.parse import urlparse
import time # Dodano import time dla pętli ponawiania prób

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

# ZAAKTUALIZOWANA FUNKCJA Z MECHANIZMEM PONAWIANIA (RETRY)
def initialize_db():
    MAX_RETRIES = 5
    RETRY_DELAY = 5 # Ustawiono 5 sekund na próbę
    
    for attempt in range(MAX_RETRIES):
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
            return # Zakończ pętlę, jeśli sukces
        
        except mysql.connector.Error as err:
            print(f"Database initialization failed (Attempt {attempt + 1}/{MAX_RETRIES}): {err}. Retrying in {RETRY_DELAY} seconds...")
            # Jeśli to ostatnia próba, nie czekaj
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    
    print("FATAL: Database initialization failed after all retries.")

# Funkcja pomocnicza do ekstrakcji ID
def _get_user_id_from_path(path):
    """Pomocnicza funkcja do ekstrakcji ID użytkownika z URL (np. /users/123)."""
    try:
        parts = path.split('/')
        if len(parts) >= 2:
            return int(parts[-1])
        return None
    except ValueError:
        return None

# --- HANDLER KLASY HTTP ---

class UserHandler(BaseHTTPRequestHandler): # Zmieniono klasę bazową
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(UserHandler, '_db_initialized'):
            initialize_db()
            UserHandler._db_initialized = True
            
    # Wymagana przez BaseHTTPRequestHandler
    def do_HEAD(self):
from http.server import BaseHTTPRequestHandler, HTTPServer
import mysql.connector
import os
import json
from urllib.parse import urlparse
import time

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


# FUNKCJA Z MECHANIZMEM PONAWIANIA (RETRY)
def initialize_db():
    MAX_RETRIES = 5
    RETRY_DELAY = 5  # Ustawiono 5 sekund na próbę

    for attempt in range(MAX_RETRIES):
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
            return  # Zakończ pętlę, jeśli sukces

        except mysql.connector.Error as err:
            print(f"Database initialization failed (Attempt {attempt + 1}/{MAX_RETRIES}): "
                  f"{err}. Retrying in {RETRY_DELAY} seconds...")
            # Jeśli to ostatnia próba, nie czekaj
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)

    print("FATAL: Database initialization failed after all retries.")


# Funkcja pomocnicza do ekstrakcji ID
def _get_user_id_from_path(path):
    """Pomocnicza funkcja do ekstrakcji ID użytkownika z URL (np. /users/123)."""
    try:
        parts = path.split('/')
        if len(parts) >= 2:
            # Zakładamy, że ID jest zawsze na końcu ścieżki
            return int(parts[-1])
        return None
    except ValueError:
        return None


# --- HANDLER KLASY HTTP ---

class UserHandler(BaseHTTPRequestHandler):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(UserHandler, '_db_initialized'):
            initialize_db()
            UserHandler._db_initialized = True
            
    # Wymagana przez BaseHTTPRequestHandler
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def _send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    # METODA DO_GET (Pobieranie statusu DB i listy użytkowników)
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/db-status':
            self._check_db_status() 
            return
            
        if parsed_path.path == '/users':
            self._list_users()
            return

        # Domyślna obsługa
        self._send_json_response(200, {"message": "Use /users (GET/POST/PUT/DELETE) or /db-status."})

    # METODA DO_POST (Tworzenie użytkownika)
    def do_POST(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/users':
            self._create_user() 
            return

        self._send_json_response(404, {"error": "Not Found"})

    # METODA DO_PUT (Edycja/Aktualizacja)
    def do_PUT(self):
        parsed_path = urlparse(self.path)
        
        user_id = _get_user_id_from_path(parsed_path.path)
        if user_id is not None:
            self._update_user(user_id)
            return

        self._send_json_response(404, {"error": "Not Found. Use PUT /users/{id}."})
    
    # METODA DO_DELETE (Usuwanie)
    def do_DELETE(self):
        parsed_path = urlparse(self.path)
        
        user_id = _get_user_id_from_path(parsed_path.path)
        if user_id is not None:
            self._delete_user(user_id)
            return

        self._send_json_response(404, {"error": "Not Found. Use DELETE /users/{id}."})
    
    # Logika dla endpointu /db-status
    def _check_db_status(self):
        try:
            conn = get_db_connection()
            conn.close()
            self._send_json_response(200, {"status": "OK", "message": "Successfully connected to MySQL container."})
        except mysql.connector.Error as err:
            self._send_json_response(500, {"status": "ERROR", "message": f"Connection failed: {err.msg}"})

    # Logika dla endpointu GET /users
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

    # LOGIKA UPDATE (PUT /users/{id})
    def _update_user(self, user_id):
        try:
            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            data = json.loads(put_data)
            
            name = data.get('name')
            email = data.get('email')
            
            if not name or not email:
                self._send_json_response(400, {"error": "Name and email are required for update."})
                return

            conn = get_db_connection()
            cursor = conn.cursor()
            sql = "UPDATE users SET name = %s, email = %s WHERE id = %s"
            cursor.execute(sql, (name, email, user_id))
            conn.commit()
            rows_affected = cursor.rowcount
            conn.close()

            if rows_affected > 0:
                self._send_json_response(200, {"message": f"User with ID {user_id} updated successfully."})
            else:
                self._send_json_response(404, {"error": f"User with ID {user_id} not found."})

        except Exception as e:
            self._send_json_response(500, {"error": f"Internal server error during update: {e}"})

    # LOGIKA DELETE (DELETE /users/{id})
    def _delete_user(self, user_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = "DELETE FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            conn.commit()
            rows_affected = cursor.rowcount
            conn.close()
            
            if rows_affected > 0:
                self._send_json_response(200, {"message": f"User with ID {user_id} deleted successfully."})
            else:
                self._send_json_response(404, {"error": f"User with ID {user_id} not found."})

        except mysql.connector.Error as err:
            self._send_json_response(500, {"error": f"Failed to delete user: {err.msg}"})
        except Exception as e:
            self._send_json_response(500, {"error": f"Internal server error: {e}"})


if __name__ == "__main__":
    httpd = HTTPServer(("", PORT), UserHandler)
    print(f"Serving simplified CRUD app on port {PORT}. DB Host: {DB_HOST}")
    httpd.serve_forever()
