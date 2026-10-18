import sqlglot
from sqlglot import exp


def validate_sql(sql):
    """
    Validate SQL before sending it to PostgreSQL.
    Only SELECT queries are allowed.
    """

    # Remove unnecessary whitespace
    sql = sql.strip()

    # Remove markdown code fences if Gemini returns them
    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")
    sql = sql.strip()

    # SQL should not be empty
    if not sql:
        return False, "SQL query is empty."

    try:
        # Parse PostgreSQL SQL
        statements = sqlglot.parse(sql, dialect="postgres")

    except Exception as e:
        return False, f"Invalid SQL syntax: {e}"

    # Only one SQL statement is allowed
    if len(statements) != 1:
        return False, "Multiple SQL statements are not allowed."

    statement = statements[0]

    # Only SELECT queries are allowed
    if not isinstance(statement, exp.Select):
        return False, "Only SELECT queries are allowed."

    return True, "SQL is safe."


if __name__ == "__main__":

    test_queries = [
        "SELECT * FROM students;",
        "SELECT name, cgpa FROM students WHERE cgpa > 8;",
        "DELETE FROM students;",
        "DROP TABLE students;",
        "UPDATE students SET cgpa = 10;",
    ]

    for query in test_queries:

        is_valid, message = validate_sql(query)

        print("\nSQL:")
        print(query)

        print("Valid:", is_valid)
        print("Message:", message)