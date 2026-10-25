
import os

import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
TIMEOUT = 15

st.set_page_config(
    page_title="LoanOps AI",
    page_icon="🏦",
    layout="wide",
)

st.title("🏦 LoanOps AI")
st.caption("AI-powered loan prediction and application monitoring")

# Verify API connection
try:
    health_response = requests.get(f"{API_URL}/health", timeout=TIMEOUT)
    health_response.raise_for_status()
    health = health_response.json()
    st.success(
        f"API connected | Model loaded: {health.get('model_loaded', False)}"
    )
except requests.RequestException:
    st.error("API is unavailable. Start the FastAPI server and retry.")
    st.caption(f"API URL: {API_URL}")
    st.stop()

# Model metrics
st.subheader("Model Performance")

try:
    report_response = requests.get(f"{API_URL}/model-report", timeout=TIMEOUT)
    report_response.raise_for_status()
    report = report_response.json()
    metrics = report.get("test_metrics", {})

    metric_columns = st.columns(5)
    for column, metric_name in zip(
        metric_columns,
        ["Accuracy", "Precision", "Recall", "F1-score", "ROC-AUC"],
    ):
        value = metrics.get(metric_name)
        with column:
            st.metric(
                metric_name,
                f"{float(value):.1%}" if value is not None else "N/A",
            )
except (requests.RequestException, ValueError, TypeError):
    st.warning("Model performance metrics could not be loaded.")

st.divider()

# Loan application form
st.subheader("Loan Application")

with st.form("loan_application"):
    col1, col2, col3 = st.columns(3)

    with col1:
        gender = st.selectbox("Gender", ["Male", "Female"])
        married = st.selectbox("Married", ["Yes", "No"])
        dependents = st.selectbox(
            "Dependents", ["0", "1", "2", "3+"]
        )
        education = st.selectbox(
            "Education", ["Graduate", "Not Graduate"]
        )

    with col2:
        self_employed = st.selectbox(
            "Self Employed", ["No", "Yes"]
        )
        applicant_income = st.number_input(
            "Applicant Income", min_value=0, value=5000, step=500
        )
        coapplicant_income = st.number_input(
            "Coapplicant Income", min_value=0, value=2000, step=500
        )
        loan_amount = st.number_input(
            "Loan Amount", min_value=1, value=150, step=10
        )

    with col3:
        loan_term = st.number_input(
            "Loan Term (months)", min_value=1, value=360, step=12
        )
        credit_history = st.selectbox("Credit History", [1, 0])
        property_area = st.selectbox(
            "Property Area", ["Urban", "Semiurban", "Rural"]
        )

    submitted = st.form_submit_button(
        "Predict Loan Status", type="primary", use_container_width=True
    )

if submitted:
    payload = {
        "Gender": gender,
        "Married": married,
        "Dependents": dependents,
        "Education": education,
        "Self_Employed": self_employed,
        "ApplicantIncome": applicant_income,
        "CoapplicantIncome": coapplicant_income,
        "LoanAmount": loan_amount,
        "Loan_Amount_Term": loan_term,
        "Credit_History": credit_history,
        "Property_Area": property_area,
    }

    try:
        response = requests.post(
            f"{API_URL}/predict", json=payload, timeout=TIMEOUT
        )
        response.raise_for_status()
        result = response.json()

        st.subheader("Prediction Result")
        prediction = int(result["prediction"])
        approval_probability = float(result["approval_probability"])

        if prediction == 1:
            st.success("Loan Status: Approved (Model Prediction)")
        else:
            st.error("Loan Status: Not Approved (Model Prediction)")

        st.metric(
            "Estimated Approval Probability",
            f"{approval_probability:.2f}%"
        )

        st.progress(approval_probability / 100)

        st.caption(
            f"Prediction ID: {result['id']} | "
            "Probability is a model estimate, not a guarantee."
        )

    except requests.RequestException as exc:
        st.error("Prediction request failed.")
        st.caption(f"Details: {type(exc).__name__}")

st.divider()


# Application Records
st.subheader("Application Records")

if st.button("Refresh Records"):
    st.rerun()

try:
    records_response = requests.get(
        f"{API_URL}/predictions?limit=500",
        timeout=TIMEOUT,
    )
    records_response.raise_for_status()
    records = records_response.json()

    # Summary counts use the records returned by the API.
    total_applications = len(records)
    approved_count = sum(
        1 for record in records if record["prediction"] == 1
    )
    not_approved_count = sum(
        1 for record in records if record["prediction"] == 0
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Applications", total_applications)
    col2.metric("Approved", approved_count)
    col3.metric("Not Approved", not_approved_count)

    st.divider()

    # Search and status filters
    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        search_id = st.text_input(
            "Search by Application ID",
            placeholder="Enter an ID, e.g. 15",
        ).strip()

    with filter_col2:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Approved", "Not Approved"],
        )

    filtered_records = records

    if search_id:
        if search_id.isdigit():
            filtered_records = [
                record for record in filtered_records
                if record["id"] == int(search_id)
            ]
        else:
            filtered_records = []

    if status_filter == "Approved":
        filtered_records = [
            record for record in filtered_records
            if record["prediction"] == 1
        ]
    elif status_filter == "Not Approved":
        filtered_records = [
            record for record in filtered_records
            if record["prediction"] == 0
        ]

    # Saved applications table
    st.markdown("### Saved Applications")

    table_rows = [
        {
            "ID": record["id"],
            "Status": record["status"],
            "Approval Probability": (
                f'{record["approval_probability"]:.2f}%'
                if record.get("approval_probability") is not None
                else "N/A"
            ),
        }
        for record in filtered_records
    ]

    st.dataframe(
        table_rows,
        use_container_width=True,
        hide_index=True,
    )

    # Full details for a selected record
    if filtered_records:
        record_ids = [record["id"] for record in filtered_records]

        selected_id = st.selectbox(
            "Select an application to view full details",
            record_ids,
            format_func=lambda record_id: f"Application #{record_id}",
        )

        selected_record = next(
            record for record in filtered_records
            if record["id"] == selected_id
        )

        with st.expander("Application Details", expanded=True):
            st.markdown(f'**Application ID:** {selected_record["id"]}')
            st.markdown(f'**Status:** {selected_record["status"]}')

            probability = selected_record.get("approval_probability")
            st.markdown(
                "**Approval Probability:** "
                + (
                    f"{probability:.2f}%"
                    if probability is not None
                    else "N/A (not stored for this older record)"
                )
            )

            st.markdown(f'**Created At (UTC):** {selected_record["created_at"]}')
            st.markdown("**Application Inputs**")

            st.json(selected_record["input"])
    else:
        st.info("No applications match the selected search and filters.")

except requests.RequestException as error:
    st.error(f"Could not load application records: {error}")
except (ValueError, KeyError, TypeError) as error:
    st.error(f"Unexpected application records response: {error}")
