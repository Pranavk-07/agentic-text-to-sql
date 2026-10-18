def create_sql_prompt(question, schema):

    prompt = f"""
You are a Text-to-SQL assistant.

Your task is to convert the user's natural language
question into a PostgreSQL SQL query.

DATABASE SCHEMA:
{schema}

USER QUESTION:
{question}

RULES:
1. Generate only a SQL SELECT query.
2. Do not generate INSERT, UPDATE, DELETE, DROP, ALTER, or TRUNCATE.
3. Use only tables and columns present in the schema.
4. Generate PostgreSQL-compatible SQL.
5. Do not use markdown code fences.
6. Return only the SQL query.

SQL:
"""

    return prompt