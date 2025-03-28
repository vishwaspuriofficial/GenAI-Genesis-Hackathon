"""
AI Server - Main Entry Point

This is the main entry point for the AI server component of the GenAI-Genesis-Hackathon project.
It integrates file processing, database operations, and agent functionality into a single RESTful API server.
"""

import os
import datetime
import json
import threading
import time
from typing import Optional
from flask import Flask, request, jsonify, make_response, send_from_directory
from flask_restful import Api, Resource
from flask_cors import CORS
from werkzeug.utils import secure_filename
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import components from the database module
from database.db_utils import query_database

# Import components from the file processing module
from file_processing.file_filter import load_documents, update_database

# Import agent functionality
from agent.agent import process_meeting_files

# Create Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16MB
api = Api(app)

# Enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Database API Resource
class DatabaseQueryResource(Resource):
    def get(self):
        """
        Search the database using vector similarity search
        """
        try:
            query = request.args.get('query')
            if not query:
                return {"error": "Missing query parameter"}, 400
                
            results = query_database(query)
            return results, 200
        except Exception as e:
            return {"error": f"Database query error: {str(e)}"}, 500

# File processing resources
class DatabaseUpdateResource(Resource):
    def post(self):
        """
        Update the database with new files
        
        This scans the raw_files directory and processes any new files,
        then updates the database with their contents.
        
        If meeting_id is provided, it will only process files for that meeting.
        """
        try:
            meeting_id = request.args.get('meeting_id')
            
            # Start the database update in a new thread to not block the response
            update_thread = threading.Thread(target=update_database)
            update_thread.daemon = True
            update_thread.start()
            
            return {
                "status": "Database update started in background", 
                "timestamp": datetime.datetime.now().isoformat()
            }, 200
        except Exception as e:
            return {"error": f"Database update error: {str(e)}"}, 500

class FileUploadResource(Resource):
    def post(self):
        """
        Upload and process a file directly
        
        The file will be saved to the raw_files directory and then processed.
        """
        try:
            # Check if file part exists in request
            if 'file' not in request.files:
                return {"error": "No file part in request"}, 400
                
            file = request.files['file']
            
            # Check if file is selected
            if file.filename == '':
                return {"error": "No file selected"}, 400
                
            # Save the uploaded file
            file_location = f"raw_files/{secure_filename(file.filename)}"
            os.makedirs("raw_files", exist_ok=True)
            
            file.save(file_location)
            
            # Process the file in a background thread
            update_thread = threading.Thread(target=update_database)
            update_thread.daemon = True
            update_thread.start()
            
            return {
                "status": "File uploaded and processing started",
                "filename": file.filename,
                "timestamp": datetime.datetime.now().isoformat()
            }, 200
        except Exception as e:
            return {"error": f"File upload error: {str(e)}"}, 500

# Agent resource
class ProcessMeetingResource(Resource):
    def post(self):
        """
        Process files for a specific meeting using the agent
        
        This will download and process all files associated with the meeting,
        and generate a response.
        """
        try:
            meeting_id = request.args.get('meeting_id')
            if not meeting_id:
                # Also check JSON body if not in query params
                data = request.get_json()
                if data and 'meeting_id' in data:
                    meeting_id = data['meeting_id']
                else:
                    return {"error": "Missing meeting_id parameter"}, 400
            
            # Call the agent to process the meeting
            result = process_meeting_files(meeting_id)
            return {
                "status": "Meeting processed",
                "meeting_id": meeting_id,
                "result": result,
                "timestamp": datetime.datetime.now().isoformat()
            }, 200
        except Exception as e:
            return {"error": f"Meeting processing error: {str(e)}"}, 500

# Health check resource
class HealthCheckResource(Resource):
    def get(self):
        """
        Simple health check endpoint
        """
        return {
            "status": "healthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "components": {
                "database": "online",
                "file_processing": "online",
                "agent": "online"
            }
        }, 200

# OpenAPI documentation resources
class OpenAPISpecResource(Resource):
    def get(self):
        """Serve the OpenAPI specification file"""
        return send_from_directory('.', 'openapi.yaml')

class SwaggerUIResource(Resource):
    def get(self):
        """Serve a Swagger UI page for API documentation"""
        swagger_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>AI Server API Documentation</title>
            <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4/swagger-ui.css">
            <style>
                body {
                    margin: 0;
                    padding: 0;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                }
                .swagger-ui .topbar {
                    background-color: #222;
                }
                .swagger-ui .info .title {
                    color: #222;
                }
            </style>
        </head>
        <body>
            <div id="swagger-ui"></div>
            
            <script src="https://unpkg.com/swagger-ui-dist@4/swagger-ui-bundle.js"></script>
            <script>
                window.onload = function() {
                    const ui = SwaggerUIBundle({
                        url: "/openapi.yaml",
                        dom_id: '#swagger-ui',
                        deepLinking: true,
                        presets: [
                            SwaggerUIBundle.presets.apis,
                            SwaggerUIBundle.SwaggerUIStandalonePreset
                        ],
                        layout: "BaseLayout"
                    });
                };
            </script>
        </body>
        </html>
        """
        response = make_response(swagger_html)
        response.headers['Content-Type'] = 'text/html'
        return response

# Register API resources
api.add_resource(DatabaseQueryResource, '/query_database')
api.add_resource(DatabaseUpdateResource, '/update_database')
api.add_resource(FileUploadResource, '/upload_file')
api.add_resource(ProcessMeetingResource, '/process_meeting')
api.add_resource(HealthCheckResource, '/health')
api.add_resource(OpenAPISpecResource, '/openapi.yaml')
api.add_resource(SwaggerUIResource, '/docs', '/api-docs')

# Run scheduled tasks in background
def run_scheduler():
    """
    Run scheduled tasks periodically in the background
    """
    while True:
        try:
            # Update database with new files
            update_database()
            print(f"[{datetime.datetime.now().isoformat()}] Scheduler: Database updated")
            
            # Sleep for 1 hour
            time.sleep(3600)
        except Exception as e:
            print(f"[{datetime.datetime.now().isoformat()}] Scheduler error: {str(e)}")
            # Sleep for 5 minutes if there was an error
            time.sleep(300)

# Start the scheduler in a daemon thread when the app starts
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

# Run the server when executed as a script
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8025))
    print(f"Starting AI Server on port {port}...")
    print(f"API documentation available at http://localhost:{port}/docs")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True) 