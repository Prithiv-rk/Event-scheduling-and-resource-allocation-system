from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import json
import os
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# MySQL Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'prithiv', 
    'database': 'event_scheduling'
}

# Database connection function
def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Initialize database and tables
def init_db():
    try:
        # First, connect without database to create it
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.close()
        connection.close()
        
        # Now connect to the database
        connection = get_db_connection()
        if connection is None:
            return
            
        cursor = connection.cursor()
        
        # Create events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create resources table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resources (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                type VARCHAR(100) NOT NULL,
                capacity INT NOT NULL,
                available INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create allocations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS allocations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                event_id INT NOT NULL,
                resource_id INT NOT NULL,
                quantity INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
                FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
                UNIQUE KEY unique_allocation (event_id, resource_id)
            )
        ''')
        
        connection.commit()
        cursor.close()
        connection.close()
        print("Database initialized successfully!")
        
    except Error as e:
        print(f"Error initializing database: {e}")

# Initialize database on startup
init_db()

@app.route('/')
def index():
    return render_template('index.html')

# API Endpoints
@app.route('/api/events', methods=['GET', 'POST'])
def handle_events():
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor(dictionary=True)
    
    if request.method == 'GET':
        cursor.execute('SELECT * FROM events ORDER BY date DESC, start_time DESC')
        events = cursor.fetchall()
        
        # Convert date and time to strings
        for event in events:
            event['date'] = str(event['date'])
            event['start_time'] = str(event['start_time'])
            event['end_time'] = str(event['end_time'])
            
        cursor.close()
        connection.close()
        return jsonify(events)
    
    elif request.method == 'POST':
        data = request.json
        
        # Validation
        if not data.get('name') or not data.get('date') or not data.get('start_time') or not data.get('end_time'):
            cursor.close()
            connection.close()
            return jsonify({'error': 'Missing required fields'}), 400
        
        try:
            cursor.execute('''
                INSERT INTO events (name, description, date, start_time, end_time)
                VALUES (%s, %s, %s, %s, %s)
            ''', (
                data['name'],
                data.get('description', ''),
                data['date'],
                data['start_time'],
                data['end_time']
            ))
            
            connection.commit()
            event_id = cursor.lastrowid
            
            cursor.execute('SELECT * FROM events WHERE id = %s', (event_id,))
            event = cursor.fetchone()
            
            # Convert date and time to strings
            event['date'] = str(event['date'])
            event['start_time'] = str(event['start_time'])
            event['end_time'] = str(event['end_time'])
            
            cursor.close()
            connection.close()
            return jsonify(event), 201
            
        except Error as e:
            cursor.close()
            connection.close()
            return jsonify({'error': str(e)}), 500

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor()
    
    try:
        cursor.execute('DELETE FROM events WHERE id = %s', (event_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'Event deleted'}), 200
        
    except Error as e:
        cursor.close()
        connection.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/resources', methods=['GET', 'POST'])
def handle_resources():
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor(dictionary=True)
    
    if request.method == 'GET':
        cursor.execute('SELECT * FROM resources ORDER BY id DESC')
        resources = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(resources)
    
    elif request.method == 'POST':
        data = request.json
        
        # Validation
        if not data.get('name') or not data.get('type') or not data.get('capacity'):
            cursor.close()
            connection.close()
            return jsonify({'error': 'Missing required fields'}), 400
        
        try:
            cursor.execute('''
                INSERT INTO resources (name, type, capacity, available)
                VALUES (%s, %s, %s, %s)
            ''', (
                data['name'],
                data['type'],
                data['capacity'],
                data['capacity']  # Initially all capacity is available
            ))
            
            connection.commit()
            resource_id = cursor.lastrowid
            
            cursor.execute('SELECT * FROM resources WHERE id = %s', (resource_id,))
            resource = cursor.fetchone()
            
            cursor.close()
            connection.close()
            return jsonify(resource), 201
            
        except Error as e:
            cursor.close()
            connection.close()
            return jsonify({'error': str(e)}), 500

@app.route('/api/resources/<int:resource_id>', methods=['DELETE'])
def delete_resource(resource_id):
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor()
    
    try:
        cursor.execute('DELETE FROM resources WHERE id = %s', (resource_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'Resource deleted'}), 200
        
    except Error as e:
        cursor.close()
        connection.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/allocations', methods=['GET', 'POST'])
def handle_allocations():
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor(dictionary=True)
    
    if request.method == 'GET':
        # Get all allocations with event and resource details
        cursor.execute('''
            SELECT 
                a.id,
                a.event_id,
                a.resource_id,
                a.quantity,
                e.name as event_name,
                e.date as event_date,
                r.name as resource_name
            FROM allocations a
            JOIN events e ON a.event_id = e.id
            JOIN resources r ON a.resource_id = r.id
            ORDER BY a.id DESC
        ''')
        
        allocations = cursor.fetchall()
        
        # Convert date to string
        for alloc in allocations:
            alloc['event_date'] = str(alloc['event_date'])
        
        cursor.close()
        connection.close()
        return jsonify(allocations)
    
    elif request.method == 'POST':
        data = request.json
        event_id = data.get('event_id')
        resource_id = data.get('resource_id')
        quantity = data.get('quantity')
        
        if not event_id or not resource_id or not quantity:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Missing required fields'}), 400
        
        try:
            # Check if event exists
            cursor.execute('SELECT id FROM events WHERE id = %s', (event_id,))
            event = cursor.fetchone()
            
            # Check if resource exists and has enough availability
            cursor.execute('SELECT id, available, name FROM resources WHERE id = %s', (resource_id,))
            resource = cursor.fetchone()
            
            if not event:
                cursor.close()
                connection.close()
                return jsonify({'error': 'Event not found'}), 404
            
            if not resource:
                cursor.close()
                connection.close()
                return jsonify({'error': 'Resource not found'}), 404
            
            if resource['available'] < quantity:
                cursor.close()
                connection.close()
                return jsonify({'error': f'Not enough resources available. Only {resource["available"]} available.'}), 400
            
            # Check if already allocated
            cursor.execute(
                'SELECT id FROM allocations WHERE event_id = %s AND resource_id = %s',
                (event_id, resource_id)
            )
            existing = cursor.fetchone()
            
            if existing:
                cursor.close()
                connection.close()
                return jsonify({'error': 'Resource already allocated to this event'}), 400
            
            # Create allocation
            cursor.execute('''
                INSERT INTO allocations (event_id, resource_id, quantity)
                VALUES (%s, %s, %s)
            ''', (event_id, resource_id, quantity))
            
            # Update resource availability
            cursor.execute('''
                UPDATE resources
                SET available = available - %s
                WHERE id = %s
            ''', (quantity, resource_id))
            
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify({'message': 'Resource allocated successfully'}), 201
            
        except Error as e:
            cursor.close()
            connection.close()
            return jsonify({'error': str(e)}), 500

@app.route('/api/allocations/<int:event_id>/<int:resource_id>', methods=['DELETE'])
def delete_allocation(event_id, resource_id):
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Get the allocation to retrieve quantity
        cursor.execute('''
            SELECT quantity FROM allocations
            WHERE event_id = %s AND resource_id = %s
        ''', (event_id, resource_id))
        
        allocation = cursor.fetchone()
        
        if not allocation:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Allocation not found'}), 404
        
        # Delete the allocation
        cursor.execute('''
            DELETE FROM allocations
            WHERE event_id = %s AND resource_id = %s
        ''', (event_id, resource_id))
        
        # Return the allocated quantity to available
        cursor.execute('''
            UPDATE resources
            SET available = available + %s
            WHERE id = %s
        ''', (allocation['quantity'], resource_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'Allocation removed'}), 200
        
    except Error as e:
        cursor.close()
        connection.close()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
