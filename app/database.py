import psycopg


def get_connection():
    return psycopg.connect(
        host="localhost",
        port=5432,
        dbname="agentsql",
        user="postgres",
        password="2004"
    )


def execute_query(query):

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(query)

        rows = cursor.fetchall()

        return rows

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":

    query = """
        SELECT name, cgpa
        FROM students
        WHERE cgpa > 8;
    """

    results = execute_query(query)

    for row in results:
        print(row)