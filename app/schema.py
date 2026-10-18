from app.database import get_connection
 
 
def get_schema():
 
    connection = get_connection()
    cursor = connection.cursor()
 
    query = """
        SELECT
            c.table_name,
            c.column_name,
            c.data_type,
            CASE
                WHEN tc.constraint_type = 'PRIMARY KEY'
                THEN 'PRIMARY KEY'
                ELSE ''
            END AS constraint_type
        FROM information_schema.columns c
 
        LEFT JOIN information_schema.key_column_usage kcu
            ON c.table_name = kcu.table_name
            AND c.column_name = kcu.column_name
            AND c.table_schema = kcu.table_schema
 
        LEFT JOIN information_schema.table_constraints tc
            ON kcu.constraint_name = tc.constraint_name
            AND kcu.table_name = tc.table_name
            AND kcu.table_schema = tc.table_schema
 
        WHERE c.table_schema = 'public'
 
        ORDER BY
            c.table_name,
            c.ordinal_position;
    """
 
    cursor.execute(query)
 
    rows = cursor.fetchall()
 
    cursor.close()
    connection.close()
 
    return rows
 
 
def format_schema(rows):
 
    schema = {}
 
    for table_name, column_name, data_type, constraint_type in rows:
 
        if table_name not in schema:
            schema[table_name] = []
 
        column_info = f"{column_name}: {data_type}"

        if constraint_type:
            column_info += f" ({constraint_type})"
 
        schema[table_name].append(column_info)
 
    result = ""
 
    for table_name, columns in schema.items():

        result += f"Table: {table_name}\n"
 
        for column in columns:
            result += f"  - {column}\n"
 
        result += "\n"
 
    return result
 
 
if __name__ == "__main__":
 
    rows = get_schema()
 
    formatted_schema = format_schema(rows)
 
    print(formatted_schema)

def get_schema_metadata():

    rows = get_schema()

    metadata = {}

    for table_name, column_name, data_type, constraint_type in rows:

        if table_name not in metadata:
            metadata[table_name] = {}

        metadata[table_name][column_name] = {
            "data_type": data_type,
            "constraint": constraint_type
        }

    return metadata