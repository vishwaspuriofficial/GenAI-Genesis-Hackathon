# AI Server

This directory contains the consolidated AI components for the GenAI-Genesis-Hackathon project. It provides a unified RESTful API for database operations, file processing, and agent functionality.

## Directory Structure

```
AI_server/
├── main.py                  # Main entry point for the RESTful API server
├── scheduler.py             # Scheduling utilities
├── database/                # Database operations
│   ├── db_utils.py          # Database utility functions
│   ├── main.py              # Database API
│   ├── upload_json_data.py  # Utilities for uploading data
│   └── vector_search_test.py # Testing for vector search
├── file_processing/         # File processing functionality
│   ├── file_filter.py       # Main file filtering logic
│   ├── database_test.py     # Testing utilities
│   ├── db_utils.py          # Database utilities for file processing
│   ├── utils.py             # Utility functions
│   └── json_files/          # JSON files for processing
└── agent/                   # Agent functionality
    └── agent.py             # Agent implementation
```

## Features

### RESTful API

The server implements a traditional RESTful API using Flask and Flask-RESTful, providing:
- Standardized endpoints with proper HTTP methods
- Standard HTTP status codes
- JSON-based request and response formats
- Resource-based URL structure

### Database API

The database component provides:
- Vector-based similarity search for document retrieval
- Integration with Firebase/Firestore for data storage
- Embeddings generation using OpenAI's text-embedding models
- JSON data upload functionality

### File Processing

The file processing component includes:
- Document loading and parsing (PDF, TXT)
- Content extraction and summarization
- Vector embeddings for document semantic search
- Database integration for document storage and retrieval

### Agent

The agent component offers:
- Meeting processing functionality
- File analysis and understanding
- Response generation for meeting requests
- Integration with the website backend

## Running the Server

To run the server:

```bash
cd AI_server
./start_server.sh
```

Or manually:

```bash
cd AI_server
python main.py
```

By default, the server runs on port 8025. You can change this by setting the `PORT` environment variable.

## API Endpoints

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/query_database` | GET | Search the database | `query`: The search query string |
| `/update_database` | POST | Update the database with new files | `meeting_id` (optional): Only process files for this meeting |
| `/upload_file` | POST | Upload and process a file | `file`: The file to upload (form data) |
| `/process_meeting` | POST | Process files for a meeting | `meeting_id`: The meeting ID to process |
| `/health` | GET | Health check endpoint | None |

## Environment Variables

The following environment variables are required:
- `OPENAI_API_KEY` - API key for OpenAI services
- `GEMINI_API_KEY` - API key for Google Gemini services (if used)
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to Firebase credentials JSON file
- `PORT` - Port for the server to listen on (default: 8025)

## Dependencies

See the requirements.txt file in this directory for all dependencies. 