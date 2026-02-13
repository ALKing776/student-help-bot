"""
Professional Web Dashboard for Student Help Bot
Flask-based admin interface with real-time monitoring
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_socketio import SocketIO, emit
import json
import threading
import time
from datetime import datetime
from typing import Dict, Any
import logging
from config import config
from database import db
from account_manager import account_manager
from analytics import analytics_engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # Change in production

# Initialize SocketIO for real-time updates
socketio = SocketIO(app, cors_allowed_origins="*")

# Authentication (simple for now - enhance for production)
VALID_PASSWORD = config.DASHBOARD_PASSWORD

class DashboardAuth:
    """Simple authentication for dashboard"""
    
    def __init__(self):
        self.authenticated_sessions = set()
    
    def authenticate(self, password: str) -> bool:
        return password == VALID_PASSWORD
    
    def is_authenticated(self, session_id: str) -> bool:
        return session_id in self.authenticated_sessions
    
    def login(self, session_id: str):
        self.authenticated_sessions.add(session_id)
    
    def logout(self, session_id: str):
        self.authenticated_sessions.discard(session_id)

auth = DashboardAuth()

# Static files and favicon
@app.route('/favicon.ico')
def favicon():
    return '', 204  # Return empty response for favicon

# Routes
@app.route('/')
def index():
    """Main dashboard page"""
    if not auth.is_authenticated(request.cookies.get('session_id', '')):
        return redirect(url_for('login'))
    
    return render_template('dashboard.html')

@app.route('/login')
def login_page():
    """Login page"""
    if auth.is_authenticated(request.cookies.get('session_id', '')):
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    """Handle login POST request"""
    password = request.form.get('password')
    if auth.authenticate(password):
        session_id = str(time.time())  # Simple session ID
        auth.login(session_id)
        response = redirect(url_for('index'))
        response.set_cookie('session_id', session_id, max_age=3600*24)  # 24 hour session
        return response
    else:
        flash('Invalid password')
        return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    """Logout endpoint"""
    session_id = request.cookies.get('session_id', '')
    auth.logout(session_id)
    response = redirect(url_for('login'))
    response.set_cookie('session_id', '', expires=0)
    return response

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    if not auth.is_authenticated(request.cookies.get('session_id', '')):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        stats = analytics_engine.get_realtime_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error in stats API: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/accounts')
def api_accounts():
    """API endpoint for account status"""
    if not auth.is_authenticated(request.cookies.get('session_id', '')):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        account_stats = account_manager.get_account_stats()
        health_summary = account_manager.get_health_summary()
        
        return jsonify({
            'accounts': account_stats,
            'health_summary': health_summary
        })
    except Exception as e:
        logger.error(f"Error in accounts API: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/users')
def api_users():
    """API endpoint for user management"""
    if not auth.is_authenticated(request.cookies.get('session_id', '')):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get recent users from database
        recent_messages = db.get_recent_messages(limit=50)
        users = {}
        
        for msg in recent_messages:
            if msg.sender_id not in users:
                users[msg.sender_id] = {
                    'id': msg.sender_id,
                    'username': msg.sender_username or 'Unknown',
                    'messages_count': 0,
                    'help_requests': 0,
                    'last_seen': msg.processed_at.isoformat() if msg.processed_at else ''
                }
            users[msg.sender_id]['messages_count'] += 1
            if msg.is_forwarded:
                users[msg.sender_id]['help_requests'] += 1
        
        return jsonify({
            'users': list(users.values()),
            'total_users': len(users)
        })
    except Exception as e:
        logger.error(f"Error in users API: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/services')
def api_services():
    """API endpoint for service statistics"""
    if not auth.is_authenticated(request.cookies.get('session_id', '')):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        service_stats = analytics_engine.get_service_statistics()
        return jsonify({
            'services': [asdict(stat) for stat in service_stats]
        })
    except Exception as e:
        logger.error(f"Error in services API: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/<report_type>')
def api_reports(report_type: str):
    """API endpoint for reports"""
    if not auth.is_authenticated(request.cookies.get('session_id', '')):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        days = int(request.args.get('days', 7))
        format_type = request.args.get('format', 'json')
        
        report = analytics_engine.generate_report(report_type, format_type, days)
        return report
    except Exception as e:
        logger.error(f"Error in reports API: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """API endpoint for configuration management"""
    if not auth.is_authenticated(request.cookies.get('session_id', '')):
        return jsonify({'error': 'Unauthorized'}), 401
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            key = data.get('key')
            value = data.get('value')
            
            if not key or value is None:
                return jsonify({'error': 'Key and value required'}), 400
            
            if config.update_setting(key, value):
                return jsonify({'success': True, 'message': f'Setting {key} updated'})
            else:
                return jsonify({'error': 'Failed to update setting'}), 500
                
        except Exception as e:
            logger.error(f"Error updating config: {e}")
            return jsonify({'error': str(e)}), 500
    
    else:  # GET request
        try:
            config_data = config.get_all_settings()
            return jsonify(config_data)
        except Exception as e:
            logger.error(f"Error getting config: {e}")
            return jsonify({'error': str(e)}), 500

# WebSocket events for real-time updates
@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    session_id = request.cookies.get('session_id', '')
    if not auth.is_authenticated(session_id):
        return False  # Reject connection
    
    logger.info(f"WebSocket client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info(f"WebSocket client disconnected: {request.sid}")

@socketio.on('request_updates')
def handle_updates_request(data):
    """Handle request for real-time updates"""
    session_id = request.cookies.get('session_id', '')
    if not auth.is_authenticated(session_id):
        return
    
    # Send initial data
    try:
        stats = analytics_engine.get_realtime_stats()
        emit('stats_update', stats)
        
        account_stats = account_manager.get_account_stats()
        emit('accounts_update', {'accounts': account_stats})
        
    except Exception as e:
        logger.error(f"Error sending updates: {e}")

# Background thread for periodic updates
def background_updates():
    """Send periodic updates to connected clients"""
    while True:
        try:
            # Get fresh data
            stats = analytics_engine.get_realtime_stats()
            account_stats = account_manager.get_account_stats()
            
            # Emit to all connected clients
            socketio.emit('stats_update', stats)
            socketio.emit('accounts_update', {'accounts': account_stats})
            
            time.sleep(30)  # Update every 30 seconds
            
        except Exception as e:
            logger.error(f"Error in background updates: {e}")
            time.sleep(30)

def start_dashboard():
    """Start the dashboard server"""
    try:
        # Start background update thread
        update_thread = threading.Thread(target=background_updates, daemon=True)
        update_thread.start()
        
        # Start Flask-SocketIO server
        socketio.run(
            app, 
            host=config.DASHBOARD_HOST,
            port=config.DASHBOARD_PORT,
            debug=False,
            allow_unsafe_werkzeug=True
        )
        
    except Exception as e:
        logger.error(f"Error starting dashboard: {e}")

if __name__ == '__main__':
    start_dashboard()