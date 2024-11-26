from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Used for session management

# Database connection
def connect_db():
    conn = sqlite3.connect('tickets.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database tables
def create_tables():
    with connect_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                issue TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT DEFAULT 'New',
                notes TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

# Default route redirects to ticket submission
@app.route('/')
def home():
    return redirect(url_for('submit_ticket'))

# Admin login route
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with connect_db() as conn:
            admin = conn.execute(
                'SELECT * FROM admin WHERE username = ? AND password = ?',
                (username, password)
            ).fetchone()
            if admin:
                session['admin'] = username
                return redirect(url_for('view_tickets'))
            else:
                return "Invalid credentials, please try again."
    return render_template('admin_login.html')

# Admin logout route
@app.route('/admin_logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

# Route for ticket submission
@app.route('/submit_ticket', methods=['GET', 'POST'])
def submit_ticket():
    if request.method == 'POST':
        name = request.form['name']
        issue = request.form['issue']
        priority = request.form['priority']
        with connect_db() as conn:
            conn.execute(
                'INSERT INTO tickets (name, issue, priority) VALUES (?, ?, ?)',
                (name, issue, priority)
            )
            conn.commit()
        return "Ticket submitted successfully!"
    return render_template('submit_ticket.html')

# Route to view tickets (admin only)
@app.route('/view_tickets')
def view_tickets():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    with connect_db() as conn:
        tickets = conn.execute('SELECT * FROM tickets ORDER BY timestamp DESC').fetchall()
    return render_template('view_tickets.html', tickets=tickets)

# Route to update ticket status and add comments
@app.route('/update_ticket/<int:ticket_id>', methods=['GET', 'POST'])
def update_ticket(ticket_id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        status = request.form['status']
        notes = request.form['notes']
        with connect_db() as conn:
            conn.execute(
                'UPDATE tickets SET status = ?, notes = ? WHERE id = ?',
                (status, notes, ticket_id)
            )
            conn.commit()
        return redirect(url_for('view_tickets'))
    with connect_db() as conn:
        ticket = conn.execute(
            'SELECT * FROM tickets WHERE id = ?', (ticket_id,)
        ).fetchone()
    return render_template('update_ticket.html', ticket=ticket)

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
