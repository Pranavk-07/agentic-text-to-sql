# Agentic Text-to-SQL

An AI-powered application that converts natural language questions into SQL queries and retrieves answers from a PostgreSQL database.

## Overview

Agentic Text-to-SQL helps users interact with structured database information using natural language instead of manually writing SQL queries.

The application uses a large language model (LLM) to help generate SQL, validates the query, executes it against the database, and presents the results in a user-friendly format.

## Features

- Convert natural language questions into SQL queries.
- Connect to a PostgreSQL database.
- Retrieve answers from database tables.
- Validate generated SQL queries before execution.
- Generate natural language answers from query results.
- Provide API endpoints using FastAPI.
- Offer a simple HTML, CSS, and JavaScript frontend.

## Tech Stack

- **Language:** Python
- **LLM:** Google Gemini API
- **Backend:** FastAPI
- **Database:** PostgreSQL
- **Frontend:** HTML, CSS, JavaScript
- **API Documentation:** Swagger UI

## Project Structure

```text
agentic-text-to-sql/
├── app/
│   ├── api.py
│   ├── agent.py
│   ├── database.py
│   ├── schema.py
│   ├── schema_validator.py
│   └── llm/
│       └── model.py
├── frontend/
│   └── index.html
├── .gitignore
├── README.md
└── requirements.txt
```

*The structure above describes the expected main files. Adjust it to match the actual files in your repository.*

## Prerequisites

- Python 3.11 or another Python version supported by your dependencies
- PostgreSQL
- A Google Gemini API key
- Git

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/agentic-text-to-sql.git
cd agentic-text-to-sql
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and configure the variables required by your application.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key
DB_HOST=localhost
DB_PORT=5432
DB_NAME=agentsql
DB_USER=postgres
DB_PASSWORD=your_database_password
```

Use the exact variable names expected by your code. Never commit your real API key or database password to GitHub.

### 5. Start PostgreSQL

Make sure your PostgreSQL service is running and your database and required tables have been created.

### 6. Run the application

Start the FastAPI server from the project root:

```bash
python -m uvicorn app.api:app --reload
```

Open the application at:

- Frontend: http://127.0.0.1:8000/
- API documentation: http://127.0.0.1:8000/docs

The frontend URL requires the FastAPI root route to serve `frontend/index.html`.

## Example Usage

Example natural language question:

> Show all students with a CGPA greater than 8.

The application can generate an appropriate SQL query, retrieve matching student records, and present the answer in natural language.

Actual results depend on the data stored in your PostgreSQL database.

## Security Notes

- Keep API keys and database credentials in environment variables.
- Do not commit `.env` files or virtual environments.
- Validate generated SQL before executing it.
- Use appropriate database permissions and restrict queries to the intended operations.

## Future Improvements

- Improve SQL validation and error handling.
- Add caching to reduce repeated LLM API calls.
- Add query history and improved frontend feedback.
- Support additional databases and more complex queries.
- Add automated tests and deployment.

## Author

Pranav Kumbhar

B.Tech – Information Technology

## License

Choose a license before distributing or reusing this project. If you have not selected one, no license has been granted by this repository.
