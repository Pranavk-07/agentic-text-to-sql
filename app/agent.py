from app.schema import get_schema, format_schema
from app.llm.model import ask_llm
from app.prompts.sql_prompt import create_sql_prompt
from app.validator import validate_sql
from app.database import execute_query
from app.schema_validator import validate_schema_usage


# ============================================================
# GENERATE SQL
# ============================================================

def generate_sql(question, schema):
    """
    Generate SQL using Gemini.
    """

    prompt = create_sql_prompt(
        question,
        schema
    )

    sql = ask_llm(prompt)

    return sql.strip()


# ============================================================
# CREATE SQL CORRECTION PROMPT
# ============================================================

def create_correction_prompt(question, schema, sql, error):
    """
    Create a prompt that tells Gemini how the previous SQL failed.
    """

    prompt = f"""
You are a PostgreSQL Text-to-SQL correction agent.

DATABASE SCHEMA:
{schema}

USER QUESTION:
{question}

PREVIOUS SQL:
{sql}

ERROR:
{error}

The previous SQL query is invalid.

Correct the SQL query.

RULES:
1. Generate only a SELECT query.
2. Use only tables and columns from the database schema.
3. Use PostgreSQL syntax.
4. Do not generate INSERT, UPDATE, DELETE, DROP, ALTER, or TRUNCATE.
5. Do not use markdown code fences.
6. Return only the corrected SQL query.
7. Make sure the corrected query answers the original user question.

CORRECTED SQL:
"""

    return prompt


# ============================================================
# FORMAT DATABASE RESULTS
# ============================================================

def format_results(results):
    """
    Convert PostgreSQL results into a simple format
    that can be passed to the LLM.
    """

    if results is None:
        return "No results were returned."

    if len(results) == 0:
        return "No rows were found."

    formatted_results = []

    for row in results:
        formatted_results.append(list(row))

    return formatted_results


# ============================================================
# CREATE NATURAL LANGUAGE ANSWER PROMPT
# ============================================================

def create_answer_prompt(question, sql, results):
    """
    Create a prompt that converts database results
    into a natural language answer.
    """

    formatted_results = format_results(results)

    prompt = f"""
You are a helpful database assistant.

Your job is to convert SQL query results
into a clear and easy-to-understand answer.

USER QUESTION:
{question}

SQL QUERY:
{sql}

DATABASE RESULTS:
{formatted_results}

RULES:
1. Answer the user's question directly.
2. Use only information present in the database results.
3. Do not invent or assume any data.
4. Do not show SQL unless the user asks for it.
5. Keep the answer concise.
6. If there are no rows, say that no matching data was found.
7. If the result contains a single number, explain what it represents.
8. If the result contains multiple rows, summarize them clearly.
9. Do not mention database implementation details.
10. Return only the natural language answer.

ANSWER:
"""

    return prompt


# ============================================================
# GENERATE NATURAL LANGUAGE ANSWER
# ============================================================

def generate_natural_language_answer(question, sql, results):
    """
    Generate a human-readable answer using Gemini.
    """

    prompt = create_answer_prompt(
        question,
        sql,
        results
    )

    answer = ask_llm(prompt)

    return answer.strip()


# ============================================================
# MAIN AGENT
# ============================================================

def run_agent(question):

    # --------------------------------------------------------
    # STEP 1: GET DATABASE SCHEMA
    # --------------------------------------------------------

    rows = get_schema()

    schema = format_schema(rows)

    print("\nDatabase Schema:")
    print("----------------")
    print(schema)

    # --------------------------------------------------------
    # STEP 2: MAXIMUM SQL ATTEMPTS
    # --------------------------------------------------------

    max_attempts = 3

    # --------------------------------------------------------
    # STEP 3: GENERATE INITIAL SQL
    # --------------------------------------------------------

    sql = generate_sql(
        question,
        schema
    )

    # --------------------------------------------------------
    # STEP 4: AGENT LOOP
    # --------------------------------------------------------

    for attempt in range(max_attempts):

        print(f"\nAttempt {attempt + 1}")
        print("================")

        print("\nGenerated SQL:")
        print(sql)

        # ====================================================
        # STEP 4A: SQL VALIDATION
        # ====================================================

        is_valid, message = validate_sql(sql)

        if not is_valid:

            print("\n❌ SQL validation failed:")
            print(message)

            if attempt == max_attempts - 1:

                return {
                    "success": False,
                    "question": question,
                    "sql": sql,
                    "results": None,
                    "answer": None,
                    "attempts": attempt + 1,
                    "error_type": "sql_validation",
                    "error": message
                }

            correction_prompt = create_correction_prompt(
                question,
                schema,
                sql,
                message
            )

            print("\n🤖 Asking Gemini to correct SQL...")

            sql = ask_llm(
                correction_prompt
            ).strip()

            continue

        print("\n✅ SQL validation passed.")

        # ====================================================
        # STEP 4B: SCHEMA VALIDATION
        # ====================================================

        schema_valid, schema_message = validate_schema_usage(sql)

        if not schema_valid:

            print("\n❌ Schema validation failed:")
            print(schema_message)

            if attempt == max_attempts - 1:

                return {
                    "success": False,
                    "question": question,
                    "sql": sql,
                    "results": None,
                    "answer": None,
                    "attempts": attempt + 1,
                    "error_type": "schema_validation",
                    "error": schema_message
                }

            correction_prompt = create_correction_prompt(
                question,
                schema,
                sql,
                schema_message
            )

            print("\n🤖 Asking Gemini to correct SQL...")

            sql = ask_llm(
                correction_prompt
            ).strip()

            continue

        print("\n✅ Schema validation passed.")

        # ====================================================
        # STEP 4C: EXECUTE SQL
        # ====================================================

        try:

            results = execute_query(sql)

            print("\n✅ SQL executed successfully.")

        except Exception as error:

            print("\n❌ Database Error:")
            print(error)

            if attempt == max_attempts - 1:

                return {
                    "success": False,
                    "question": question,
                    "sql": sql,
                    "results": None,
                    "answer": None,
                    "attempts": attempt + 1,
                    "error_type": "database",
                    "error": str(error)
                }

            correction_prompt = create_correction_prompt(
                question,
                schema,
                sql,
                str(error)
            )

            print("\n🤖 Sending database error to Gemini...")

            sql = ask_llm(
                correction_prompt
            ).strip()

            continue

        # ====================================================
        # STEP 4D: NATURAL LANGUAGE ANSWER
        # ====================================================

        try:

            print("\n🤖 Generating natural language answer...")

            answer = generate_natural_language_answer(
                question,
                sql,
                results
            )

            print("\nNatural Language Answer:")
            print("----------------")
            print(answer)

        except Exception as error:

            print("\n⚠️ LLM Answer Generation Error:")
            print(error)

            return {
                "success": True,
                "question": question,
                "sql": sql,
                "results": results,
                "answer": None,
                "attempts": attempt + 1,
                "error_type": "llm_answer",
                "error": str(error)
            }

        # ====================================================
        # STEP 4E: SUCCESSFUL RESPONSE
        # ====================================================

        return {
            "success": True,
            "question": question,
            "sql": sql,
            "results": results,
            "answer": answer,
            "attempts": attempt + 1,
            "error_type": None,
            "error": None
        }

    # --------------------------------------------------------
    # AGENT FAILED
    # --------------------------------------------------------

    return {
        "success": False,
        "question": question,
        "sql": sql,
        "results": None,
        "answer": None,
        "attempts": max_attempts,
        "error_type": "agent",
        "error": "Agent failed"
    }


# ============================================================
# TEST PROGRAM
# ============================================================

if __name__ == "__main__":

    question = "How many students are there in each branch?"

    response = run_agent(question)

    print("\n")
    print("=" * 50)
    print("FINAL AGENT RESPONSE")
    print("=" * 50)

    print("\nQuestion:")
    print(response["question"])

    print("\nSQL:")
    print(response["sql"])

    print("\nStatus:")

    if response["success"]:
        print("SUCCESS")
    else:
        print("FAILED")

    print("\nAttempts:")
    print(response["attempts"])

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    if response["results"] is not None:

        print("\nResults:")
        print("----------------")

        for row in response["results"]:
            print(row)

    # --------------------------------------------------------
    # ANSWER
    # --------------------------------------------------------

    if response["answer"] is not None:

        print("\nAnswer:")
        print("----------------")
        print(response["answer"])

    # --------------------------------------------------------
    # ERROR
    # --------------------------------------------------------

    if response["error"] is not None:

        print("\nError Type:")
        print("----------------")
        print(response["error_type"])

        print("\nError:")
        print("----------------")
        print(response["error"])