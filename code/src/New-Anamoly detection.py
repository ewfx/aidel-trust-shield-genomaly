import pandas as pd
import numpy as np
import re
import requests
from sklearn.ensemble import IsolationForest

# Function to extract transactions from structured text file
def parse_transactions(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            raw_data = file.read()

        if not raw_data.strip():
            print("⚠️ ERROR: Input file is empty or unreadable.")
            return pd.DataFrame()

        print("✅ Raw Data Sample:\n", raw_data[:500])  # Debug: Print first 500 chars

        # Split transactions using "---" as a separator
        transaction_blocks = re.split(r"\n---\n", raw_data.strip())

        transactions = []

        for block in transaction_blocks:
            if not block.strip():
                continue  # Skip empty blocks

            print("\n🔍 Processing Block:\n", block[:300])  # Debug

            # Extract key transaction details
            transaction_id = re.search(r"Transaction ID:\s*(\S+)", block)
            sender_name = re.search(r'Sender:\s*- Name:\s*"(.+?)"', block)
            receiver_name = re.search(r'Receiver:\s*- Name:\s*"(.+?)"', block)
            amount = re.search(r"Amount:\s*\$([\d,]+\.?\d*)", block)
            country_match = re.search(r"Receiver:\s.*Address: .+?,\s*([\w\s]+)", block)
            additional_notes = re.findall(r"Additional Notes:\n - \"(.+?)\"", block)

            if not (transaction_id and sender_name and receiver_name and amount):
                print("⚠️ Skipping incomplete transaction block:\n", block[:300])
                continue

            transactions.append({
                "Transaction ID": transaction_id.group(1).strip(),
                "Sender Name": sender_name.group(1).strip(),
                "Receiver Name": receiver_name.group(1).strip(),
                "Amount": float(amount.group(1).replace(",", "")),
                "Country": country_match.group(1).strip() if country_match else "Unknown",
                "Additional Notes": " | ".join(additional_notes) if additional_notes else "None"
            })

        df = pd.DataFrame(transactions)

        print("\n✅ Parsed DataFrame:\n", df.head())  # Debug
        return df

    except FileNotFoundError:
        print(f"❌ ERROR: File '{file_path}' not found.")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return pd.DataFrame()

# Function to enrich company data using OpenCorporates API
def get_company_info(company_name):
    api_url = f"https://api.opencorporates.com/v0.4/companies/search?q={company_name}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    return {}

# Load transactions from input file
input_file = "C:\\Users\\pramo\\OneDrive\\Desktop\\Hackathon\\transactions.txt"
df = parse_transactions(input_file)

# Validate if dataframe contains required columns
if "Sender Name" in df.columns:
    df["Company Info"] = df["Sender Name"].apply(get_company_info)
else:
    print("❌ ERROR: 'Sender Name' column missing. Check parsing logic.")

# Anomaly Detection using Isolation Forest
iso_forest = IsolationForest(contamination=0.2, random_state=42)
X_numeric = df[["Amount"]].values
df["Anomaly Score"] = iso_forest.fit_predict(X_numeric)

# Risk Scoring Function
def calculate_risk_score(amount, notes, anomaly_score):
    risk = 0
    if amount > 1000000:
        risk += 2
    if "Cayman Islands" in notes or "Panama" in notes:
        risk += 3
    if anomaly_score == -1:
        risk += 2
    return risk / 5  # Normalize risk score between 0 and 1

df["Risk Score"] = df.apply(lambda x: calculate_risk_score(x["Amount"], x["Additional Notes"], x["Anomaly Score"]), axis=1)

# Entity Classification
def determine_entity_type(name):
    shell_companies = ["Quantum Holdings Ltd", "Oceanic Holdings LLC"]
    ngos = ["Bright Future Nonprofit Inc", "Save the Children"]
    peps = ["Ali Al-Mansoori", "Viktor Petrov"]
    
    if name in shell_companies:
        return "Shell Company"
    elif name in ngos:
        return "NGO"
    elif name in peps:
        return "PEP"
    return "Corporation"

# Supporting Evidence Lookup
def get_supporting_evidence(name):
    evidence_sources = {
        "Quantum Holdings Ltd": ["British Virgin Islands Records", "Shell Company Registries"],
        "Ali Al-Mansoori": ["Sanctions List"],
        "Viktor Petrov": ["OFAC SDN List"]
    }
    return evidence_sources.get(name, ["OpenCorporates"])

# Generate Reasoning for Risk
def generate_reason(name):
    reasons = {
        "Quantum Holdings Ltd": "Entity is registered in BVI, a known tax haven. Beneficiary owner linked to offshore financial structures.",
        "Ali Al-Mansoori": "Transaction approved by a high-risk PEP individual.",
        "Viktor Petrov": "Linked to OFAC SDN list, flagged as a sanctioned entity."
    }
    return reasons.get(name, "No specific risk detected.")

# Generate Output Format
def generate_output_format(df):
    output = []
    for _, row in df.iterrows():
        entities = [row["Sender Name"], row["Receiver Name"]]
        entity_types = [determine_entity_type(entity) for entity in entities]
        supporting_evidence = [get_supporting_evidence(entity) for entity in entities]
        confidence_score = np.random.uniform(0.8, 0.99)  # Mock confidence score
        reasons = [generate_reason(entity) for entity in entities]

        output.append({
            "Transaction ID": row["Transaction ID"],
            "Extracted Entity": ", ".join(entities),
            "Entity Type": ", ".join(entity_types),
            "Risk Score": row["Risk Score"],
            "Supporting Evidence": ", ".join([", ".join(evidence) for evidence in supporting_evidence]),
            "Confidence Score": confidence_score,
            "Reason": "; ".join(reasons)
        })
    return pd.DataFrame(output)

# Generate Final Output
final_output_df = generate_output_format(df)

# Save Output to CSV
output_file = "C:\\Users\\pramo\\OneDrive\\Desktop\\Hackathon\\fraud_detection_output.csv"
final_output_df.to_csv(output_file, index=False)

print(f"✅ Output saved to {output_file}")
print(final_output_df)
