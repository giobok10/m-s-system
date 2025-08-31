from flask_socketio import emit, join_room, leave_room
from flask_login import current_user

def register_socket_events(socketio):
    
    @socketio.on('connect')
    def on_connect():
        if current_user.is_authenticated:
            if current_user.role == 'cook':
                join_room('kitchen')
            elif current_user.role == 'waiter':
                join_room('waiters')
            elif current_user.role == 'admin':
                join_room('admin')
    
    @socketio.on('disconnect')
    def on_disconnect():
        if current_user.is_authenticated:
            if current_user.role == 'cook':
                leave_room('kitchen')
            elif current_user.role == 'waiter':
                leave_room('waiters')
            elif current_user.role == 'admin':
                leave_room('admin')
