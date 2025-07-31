import json
import sqlite3
import os
from datetime import datetime
from weather_simple import WeatherSimple
from event_filter import EventFilter

def handler(event, context):
    """Netlify Function for API endpoints"""
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
    }
    
    # Handle preflight requests
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    path = event['path']
    
    try:
        if path == '/api/events':
            return get_events(headers)
        elif path == '/api/filter':
            return filter_events(event, headers)
        elif path == '/api/weather':
            return get_weather(headers)
        elif path == '/health':
            return health_check(headers)
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Endpoint not found'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }

def get_events(headers):
    """Get all events with weather data"""
    try:
        # Get weather data
        weather_api = WeatherSimple()
        weather_data = weather_api.get_weather_forecast()
        
        # Get events from database
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM events 
            WHERE date >= date('now') 
            ORDER BY date ASC, time ASC
        ''')
        events = cursor.fetchall()
        conn.close()
        
        # Filter events by weather
        event_filter = EventFilter()
        filtered_events = event_filter.filter_events_by_weather(events, weather_data)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'events': filtered_events,
                'weather': weather_data
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }

def filter_events(event, headers):
    """Filter events based on parameters"""
    try:
        # Parse query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        
        category = query_params.get('category', '')
        city = query_params.get('city', '')
        indoor_only = query_params.get('indoor_only', '')
        outdoor_only = query_params.get('outdoor_only', '')
        free_only = query_params.get('free_only', '')
        parking_required = query_params.get('parking_required', '')
        child_friendly = query_params.get('child_friendly', '')
        
        # Build query
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        
        query = 'SELECT * FROM events WHERE 1=1'
        params = []
        
        if indoor_only:
            query += ' AND is_indoor = 1'
        if outdoor_only:
            query += ' AND is_indoor = 0'
        if free_only:
            query += ' AND is_free = 1'
        if parking_required:
            query += ' AND has_parking = 1'
        if child_friendly:
            query += ' AND child_friendly = 1'
        if category:
            query += ' AND category = ?'
            params.append(category)
        if city:
            query += ' AND (location LIKE ? OR location LIKE ?)'
            params.append(f'%{city}%')
            params.append(f'%（{city}）%')
        
        cursor.execute(query, params)
        events = cursor.fetchall()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'events': events})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }

def get_weather(headers):
    """Get weather data"""
    try:
        weather_api = WeatherSimple()
        weather_data = weather_api.get_weather_forecast()
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(weather_data)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }

def health_check(headers):
    """Health check endpoint"""
    try:
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM events')
        event_count = cursor.fetchone()[0]
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'database': 'connected',
                'events_count': event_count,
                'version': '1.0.0'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        } 