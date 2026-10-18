 
import re

from app.schema import get_schema, format_schema


# ============================================================
# FORBIDDEN SQL KEYWORDS
# ============================================================

FORBIDDEN_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "TRUNCATE",
    "ALTER",
    "CREATE",
    "GRANT",
    "REVOKE"
]


# ============================================================
# SQL SAFETY VALIDATION
# ============================================================

def check_sql_safety(sql):
    """
    Check whether the SQL contains dangerous operations.
    """

    if not sql or not sql.strip():
        return False, "SQL query is empty"

    sql_upper = sql.upper()

    for keyword in FORBIDDEN_KEYWORDS:

        pattern = r"\b" + keyword + r"\b"

        if re.search(pattern, sql_upper):

            return False, (
                f"Forbidden SQL operation: {keyword}"
            )

    return True, "SQL is safe"


# ============================================================
# EXTRACT TABLES
# ============================================================

def extract_tables(sql):
    """
    Extract table names appearing after FROM and JOIN.
    """

    pattern = r"""
        \b
        (?:FROM|JOIN)
        \s+
        (?:
            [a-zA-Z_][a-zA-Z0-9_]*
            \.
        )?
        ([a-zA-Z_][a-zA-Z0-9_]*)
    """

    matches = re.findall(
        pattern,
        sql,
        flags=re.IGNORECASE | re.VERBOSE
    )

    return matches


# ============================================================
# VALIDATE TABLES
# ============================================================

def validate_tables(sql, schema):
    """
    Check whether tables used in SQL
    exist in the database schema.
    """

    tables = extract_tables(sql)

    if not tables:

        return False, "No table found in SQL query"

    # schema can be:
    #
    # {
    #     "students": ["id", "name", "branch"]
    # }
    #
    # OR
    #
    # {
    #     "students": [
    #         {"column": "id", "type": "integer"}
    #     ]
    # }
    #
    # We only need table names here.

    available_tables = set(
        table.lower()
        for table in schema.keys()
    )

    for table in tables:

        if table.lower() not in available_tables:

            return False, (
                f"Table '{table}' does not exist "
                "in the database schema"
            )

    return True, "All tables are valid"


# ============================================================
# EXTRACT SELECT COLUMNS
# ============================================================

def extract_columns(sql):
    """
    Extract simple columns from the SELECT section.
    """

    columns = []

    select_match = re.search(
        r"\bSELECT\s+(.*?)\s+\bFROM\b",
        sql,
        flags=re.IGNORECASE | re.DOTALL
    )

    if not select_match:

        return columns

    select_part = select_match.group(1).strip()

    # SELECT *
    if select_part == "*":

        return columns

    # Split columns by comma
    parts = select_part.split(",")

    for part in parts:

        column = part.strip()

        # Remove AS aliases
        column = re.split(
            r"\s+AS\s+",
            column,
            flags=re.IGNORECASE
        )[0].strip()

        # Remove normal aliases
        tokens = column.split()

        if len(tokens) > 1:

            column = tokens[0]

        # Ignore SQL functions
        if "(" in column:

            continue

        # Remove table prefix
        if "." in column:

            column = column.split(".")[-1]

        # Remove quotes
        column = column.strip('"').strip("'")

        if column:

            columns.append(column)

    return columns


# ============================================================
# GET COLUMN NAMES FROM SCHEMA
# ============================================================

def get_column_names(table_schema):
    """
    Convert different schema formats into
    a simple set of column names.

    Supports:

    ["id", "name", "branch"]

    OR:

    [
        {"column": "id", "type": "integer"},
        {"column": "name", "type": "text"}
    ]
    """

    columns = set()

    for column in table_schema:

        # ----------------------------------------
        # Format 1:
        # "id"
        # ----------------------------------------

        if isinstance(column, str):

            columns.add(column.lower())

        # ----------------------------------------
        # Format 2:
        # {"column": "id", "type": "integer"}
        # ----------------------------------------

        elif isinstance(column, dict):

            if "column" in column:

                columns.add(
                    column["column"].lower()
                )

    return columns


# ============================================================
# VALIDATE COLUMNS
# ============================================================

def validate_columns(sql, schema):
    """
    Check whether columns used in SELECT
    exist in the referenced tables.
    """

    tables = extract_tables(sql)

    if not tables:

        return False, "No table found in SQL query"

    columns = extract_columns(sql)

    # SELECT *
    if not columns:

        return True, "SELECT * does not require column validation"

    # ----------------------------------------
    # Collect columns from referenced tables
    # ----------------------------------------

    available_columns = set()

    for table in tables:

        table_key = None

        for schema_table in schema.keys():

            if schema_table.lower() == table.lower():

                table_key = schema_table

                break

        if table_key is None:

            return False, (
                f"Table '{table}' does not exist "
                "in schema"
            )

        table_columns = get_column_names(
            schema[table_key]
        )

        available_columns.update(
            table_columns
        )

    # ----------------------------------------
    # Check each SQL column
    # ----------------------------------------

    for column in columns:

        column_lower = column.lower()

        if column_lower not in available_columns:

            return False, (
                f"Column '{column}' does not exist "
                "in the referenced tables"
            )

    return True, "All columns are valid"


# ============================================================
# MAIN SCHEMA VALIDATION
# ============================================================

def validate_schema_usage(sql):
    """
    Validate tables and columns used by SQL
    against the PostgreSQL database schema.
    """

    # Get current database schema
    rows = get_schema()

    if not rows:

        return False, "Database schema is empty"

    # ----------------------------------------
    # IMPORTANT
    # ----------------------------------------
    #
    # Your existing format_schema() is mainly
    # for displaying the schema to Gemini.
    #
    # We build a simple Python dictionary
    # directly from get_schema() here.
    #
    # Expected rows:
    #
    # (
    #     table_name,
    #     column_name,
    #     data_type
    # )
    #
    # ----------------------------------------

    schema = {}

    for row in rows:

        table_name = row[0]
        column_name = row[1]

        if table_name not in schema:

            schema[table_name] = []

        schema[table_name].append(
            column_name
        )

    # ----------------------------------------
    # Validate tables
    # ----------------------------------------

    valid, message = validate_tables(
        sql,
        schema
    )

    if not valid:

        return False, message

    # ----------------------------------------
    # Validate columns
    # ----------------------------------------

    valid, message = validate_columns(
        sql,
        schema
    )

    if not valid:

        return False, message

    return True, "Schema usage is valid"


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print("SQL SCHEMA VALIDATOR TEST")
    print("================================")

    test_queries = [

        "SELECT * FROM students",

        "SELECT name FROM students",

        "SELECT branch FROM students",

        "SELECT wrong_column FROM students",

        "SELECT * FROM wrong_table",

        "DELETE FROM students"
    ]

    for sql in test_queries:

        print("\nSQL:")
        print(sql)

        # Safety test
        safe, safety_message = check_sql_safety(sql)

        if not safe:

            print("Result: ❌ INVALID")
            print("Reason:", safety_message)

            continue

        # Schema test
        valid, message = validate_schema_usage(sql)

        if valid:

            print("Result: ✅ VALID")
            print("Message:", message)

        else:

            print("Result: ❌ INVALID")
            print("Reason:", message)

 