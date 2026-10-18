from app.schema import get_schema, format_schema
from app.llm.model import ask_llm
from app.prompts.sql_prompt import create_sql_prompt
from app.safe_executor import safe_execute


def generate_sql(question):

    # Get database schema
    rows = get_schema()

    # Convert schema to text
    schema = format_schema(rows)

    # Create prompt
    prompt = create_sql_prompt(question, schema)

    # Ask Gemini
    sql = ask_llm(prompt)

    return sql


def process_question(question):

    # Step 1: Generate SQL
    sql = generate_sql(question)

    print("\nGenerated SQL:")
    print(sql)

    # Step 2: Validate and execute
    results = safe_execute(sql)

    return results


if __name__ == "__main__":

    question = "Show IT students with CGPA greater than 8."

    try:

        results = process_question(question)

        print("\nQuery Results:")

        for row in results:
            print(row)

    except Exception as e:

        print("\nError:")
        print(e)