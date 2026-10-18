from app.validator import validate_sql
from app.database import execute_query


def safe_execute(sql):

    # Step 1: Validate SQL
    is_valid, message = validate_sql(sql)

    if not is_valid:
        raise ValueError(f"SQL rejected: {message}")

    # Step 2: Execute only validated SQL
    results = execute_query(sql)

    return results


if __name__ == "__main__":

    sql = """
     SELECT *  FROM students;
"""
    
    
    
    

    try:

        results = safe_execute(sql)

        print("\nQuery Results:")

        for row in results:
            print(row)

    except Exception as e:

        print("\nError:")
        print(e)