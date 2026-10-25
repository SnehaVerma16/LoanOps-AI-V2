
from pathlib import Path
import sqlite3
import json
from datetime import datetime, timezone

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "loan_pipeline.joblib"
REPORT_PATH = BASE_DIR / "model_report.json"
DB_PATH = BASE_DIR / "loanops.db"

app = FastAPI(title="LoanOps AI", version="1.0.0")

# Load the trained pipeline once when the API starts.
model = joblib.load(MODEL_PATH)

with REPORT_PATH.open("r", encoding="utf-8") as file:
    model_report = json.load(file)



from typing import Literal
from pydantic import BaseModel, Field


class LoanApplication(BaseModel):
    Gender: Literal["Female", "Male"]
    Married: Literal["No", "Yes"]
    Dependents: Literal["0", "1", "2", "3+"]
    Education: Literal["Graduate", "Not Graduate"]
    Self_Employed: Literal["No", "Yes"]

    ApplicantIncome: float = Field(ge=0, allow_inf_nan=False)
    CoapplicantIncome: float = Field(ge=0, allow_inf_nan=False)
    LoanAmount: float = Field(gt=0, allow_inf_nan=False)
    Loan_Amount_Term: int = Field(gt=0)    
    Credit_History: int = Field(ge=0, le=1)

    Property_Area: Literal["Rural", "Semiurban", "Urban"]


def get_connection():
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                input_json TEXT NOT NULL,
                prediction INTEGER NOT NULL
            )
        """)
        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(predictions)"
            ).fetchall()
        }

        if "approval_probability" not in columns:
            connection.execute(
                "ALTER TABLE predictions "
                "ADD COLUMN approval_probability REAL"
            )


init_db()


@app.get("/")
def root():
    return {"message": "LoanOps AI API is running"}


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "database": DB_PATH.name
    }


@app.get("/model-report")
def get_model_report():
    return model_report


@app.post("/predict")
def predict(application: LoanApplication):
    try:
        input_data = application.model_dump()
        frame = pd.DataFrame([input_data])
        prediction = int(model.predict(frame)[0])

        # Probability that the loan status is approved (class 1)
        classes = list(model.named_steps["classifier"].classes_)
        probabilities = model.predict_proba(frame)[0]

        class_probabilities = {
            int(label): float(probability)
            for label, probability in zip(classes, probabilities)
        }

        approval_probability = class_probabilities[1] * 100        
        created_at = datetime.now(timezone.utc).isoformat()

        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO predictions
                    (created_at, input_json, prediction, approval_probability)
            VALUES (?, ?, ?, ?)
            """,
            (
                created_at,
                json.dumps(input_data),
                prediction,
                round(approval_probability, 2),
            ),
        )
        prediction_id = cursor.lastrowid

        return {
            "id": prediction_id,
            "prediction": prediction,
            "approval_probability": round(approval_probability, 2),
            "created_at": created_at
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {type(exc).__name__}"
        ) from exc



@app.get("/predictions")
def get_predictions(limit: int = Query(default=100, ge=1, le=500)):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, created_at, input_json, prediction,
                   approval_probability
            FROM predictions
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        {
            "id": row["id"],
            "created_at": row["created_at"],
            "input": json.loads(row["input_json"]),
            "prediction": row["prediction"],
            "approval_probability": row["approval_probability"],
            "status": (
                "Approved" if row["prediction"] == 1
                else "Not Approved"
            ),
        }
        for row in rows
    ]

