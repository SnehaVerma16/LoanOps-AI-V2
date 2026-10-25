# 🏦 LoanOps AI V2 — Intelligent Loan Prediction & Application Monitoring

An AI-powered loan prediction system that estimates loan approval probability using Machine Learning and provides an interactive dashboard to manage and monitor loan applications.

🔗 **Live Dashboard:** https://loanops-ai-dashboard-v2.onrender.com/  
🔗 **Live API:** https://loanops-ai-v2.onrender.com/  
🔗 **API Documentation:** https://loanops-ai-v2.onrender.com/docs

---

## 📌 Overview

LoanOps AI V2 combines a trained Machine Learning pipeline, a FastAPI backend, and a Streamlit dashboard to simplify loan application assessment.

Users can enter applicant details, receive a predicted loan status and estimated approval probability, and review previously saved applications.

The system is designed as an end-to-end ML deployment project demonstrating model inference, API development, input validation, database integration, and interactive data visualization.

## ✨ Features

- **Loan Status Prediction:** Predicts whether a loan application is likely to be approved or rejected.
- **Approval Probability:** Displays the model-estimated probability of approval.
- **Interactive Dashboard:** Provides a user-friendly interface for submitting applications and viewing results.
- **Application Monitoring:** Displays saved applications with application IDs, status, probability, and timestamps.
- **Search and Filtering:** Find applications by ID and filter them by prediction status.
- **Input Validation:** Validates applicant details and rejects invalid inputs through the API.
- **Model Performance Monitoring:** Displays key evaluation metrics.
- **REST API:** Exposes prediction and application-history endpoints using FastAPI.
- **SQLite Integration:** Stores prediction records locally in a SQLite database.

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Machine Learning | Scikit-learn |
| Model | Tuned Logistic Regression |
| Data Processing | NumPy, Pandas |
| Backend | FastAPI |
| API Server | Uvicorn |
| Frontend Dashboard | Streamlit |
| Database | SQLite |
| Model Serialization | Joblib |
| Deployment | Render |
| Version Control | Git and GitHub |

## 🤖 Machine Learning Model

The application uses a trained Scikit-learn pipeline with a tuned Logistic Regression classifier.

### Input Features

The model uses 11 applicant features:

- Gender
- Marital Status
- Number of Dependents
- Education
- Self-Employment Status
- Applicant Income
- Co-applicant Income
- Loan Amount
- Loan Term
- Credit History
- Property Area

### Preprocessing

- Missing numeric values are handled using median imputation.
- Numeric features are standardized using `StandardScaler`.
- Missing categorical values are handled using most-frequent imputation.
- Categorical variables are encoded using `OneHotEncoder`.
- Unknown categorical values are handled using `handle_unknown="ignore"`.

The deployed pipeline applies preprocessing and prediction consistently.

## 📊 Model Performance

The following metrics are from the model's evaluation report.

| Metric | Score |
|---|---:|
| Accuracy | 85.37% |
| Precision | 83.17% |
| Recall | 98.82% |
| F1-Score | 90.32% |
| ROC-AUC | 84.52% |

**Note:** These are evaluation metrics, not guarantees of real-world lending performance. Approval probabilities are estimates produced by the model and should not be treated as financial advice or actual lending decisions.

## 🏗️ System Architecture

```text
User
  |
  v
Streamlit Dashboard
  |
  | HTTP Requests
  v
FastAPI Backend
  |
  v
Input Validation
  |
  v
Trained ML Pipeline
  |
  v
Prediction + Approval Probability
  |
  v
SQLite Database
  |
  v
Application History Dashboard
```

## 📂 Project Structure

```text
LoanOps-AI-V2/
│
├── main.py                 # FastAPI backend and prediction endpoints
├── dashboard.py            # Streamlit dashboard
├── loan_pipeline.joblib    # Trained ML pipeline
├── model_report.json       # Model evaluation metrics
├── requirements.txt        # Python dependencies
├── .gitignore              # Excluded files and local artifacts
└── README.md               # Project documentation
```

The SQLite database (`loanops.db`) is created locally by the application and is excluded from version control.

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/SnehaVerma16/LoanOps-AI-V2.git
cd LoanOps-AI-V2
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the FastAPI backend

```bash
uvicorn main:app --reload
```

API documentation:

http://127.0.0.1:8000/docs

### 5. Start the Streamlit dashboard

Open a second terminal, activate the same virtual environment, and run:

**Windows PowerShell:**

```powershell
$env:API_URL="http://127.0.0.1:8000"
streamlit run dashboard.py
```

The dashboard will typically be available at:

http://localhost:8501

Keep the backend running while using the dashboard.

## 🔌 API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |
| GET | `/model-report` | Model evaluation report |
| POST | `/predict` | Predict loan status and save the result |
| GET | `/predictions` | Retrieve saved prediction records |

Interactive API documentation is available at `/docs`.

## ☁️ Deployment

The project is deployed on Render using two services:

1. **FastAPI Web Service:** Handles model inference and application-record operations.
2. **Streamlit Web Service:** Provides the interactive dashboard and communicates with the backend through the `API_URL` environment variable.

### Deployment URLs

- Dashboard: https://loanops-ai-dashboard-v2.onrender.com/
- Backend: https://loanops-ai-v2.onrender.com/
- API Docs: https://loanops-ai-v2.onrender.com/docs

**Deployment note:** The current deployment uses SQLite on Render's free service. Its filesystem is ephemeral, so database records may be lost when the service restarts or is redeployed. Persistent database storage would be needed for reliable long-term record retention.

## 🔮 Future Improvements

- Persistent cloud database integration.
- Model drift and prediction-distribution monitoring.
- Improved explainability using SHAP or feature-contribution analysis.
- Authentication and role-based access control.
- Automated model retraining and evaluation.
- Improved prediction calibration and out-of-distribution input checks.
- Automated testing and continuous integration.

## 👩‍💻 Author

**Sneha Verma**  
B.Tech — Computer Science and Engineering

GitHub: [@SnehaVerma16](https://github.com/SnehaVerma16)

---

## ⚠️ Disclaimer

LoanOps AI is an educational and portfolio project. Its predictions are generated by a Machine Learning model and must not be used as the sole basis for real-world loan approval or rejection decisions.
