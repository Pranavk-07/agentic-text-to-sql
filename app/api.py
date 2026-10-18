from pathlib import Path
from fastapi.responses import FileResponse
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Agentic Text-to-SQL API",
    description="Convert natural-language questions into SQL database results.",
    version="1.0.0",
)


class QuestionRequest(BaseModel):
    question: str


 
 
 

@app.get("/", include_in_schema=False)
def home():
    html_file = (
        Path(__file__).resolve().parent.parent
        / "frontend"
        / "index.html"
    )
    return FileResponse(html_file)



    


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        # Import here to keep API startup independent
        # of agent initialization.
        from app.agent import run_agent

        results = run_agent(question)

        return {
            "question": question,
            "results": results,
        }

    except Exception as exc:
        # Avoid exposing internal database/API details
        # in the response returned to the client.
        print(f"Agent error: {exc}")
        raise HTTPException(
            status_code=500,
            detail="The agent could not process the question. Check the server logs.",
        ) from exc
