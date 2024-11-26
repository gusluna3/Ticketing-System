import sqlite3

def add_admin(username, password):
    conn = sqlite3.connect('tickets.db')  # Connect to the database
    cursor = conn.cursor()
    
    # Check if the username already exists
    cursor.execute("SELECT * FROM admin WHERE username = ?", (username,))
    existing_admin = cursor.fetchone()
    
    if existing_admin:
        print(f"Admin with username '{username}' already exists!")
    else:
        # Insert the new admin user
        conn.execute('''
            INSERT INTO admin (username, password) 
            VALUES (?, ?)
        ''', (username, password))
        conn.commit()
        print(f"Admin account created! Username: {username}")
    
    conn.close()

# Replace with your desired username and password
add_admin('admin', 'password123')  # Change 'admin' and 'password123' if needed
