import streamlit as st
import pandas as pd
import gspread
import json
import os

st.set_page_config(page_title="Disease Diagnosis", page_icon="🏥")

# Function to get data from Google Sheets
def get_data_from_sheets():
    # Set up credentials
    credentials_dict = {
        "type": "service_account",
        "project_id": "disease-database-407312",
        "private_key_id": "8ef099551eb58a9e1fc07d7e0dfcb0299ddcf93b",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC6GTc+w/1KIbjF\nvPdpaAZ6JWtnvjudNGVd48fGoT43q6hHTDShOfi3Z5i+ZjNa1ftzHjHgEF1gXifB\nZU5l4NucP4HuLT7X12YoYZ6hHirqBhWSW83ljbj3m2UgROf1ioME82hNez6Glag9\nEqx0P72Cl1bZpkXj+mpEX2/Cb0r7aYgp/c9h4fybK/mmtEsrCqRs1XJBFMoScCYk\nUzs7G7CjOCkae62vOnU0cWhusP1q5hIeooe+uPi12Lu1/KK5hVwvYazC3lxwRxUT\naN5/cVihaDaGZ6Yqd+y7tnKvJN/ACmK/usAY2g1i00HoIY+qEk/uu5AMYzpzWDSR\nagOCB1azAgMBAAECggEAQemkc4qfL555/y9Kwf6iLKkMPZZXLvrb3EFNBMEfdEBM\nPdRz35bUzMDYjLdOASJBCSjsqVuidvtiQVFMTzExF0o3DtDfrTsRZ8QLly1ELdcx\n1MDHUEK9/JUBYEiHj6Qbe6lqi+bW4nwnNlpi0lmxGYvYqwYFQxXyhXz37HnWqOzB\nOnHM2Ie3AUm8+s1n8l0CEri8XVeFaaODXnL4Z4ugBdw3cazpxnzU55MG9fe7SwbE\n/yxHSQQCHbIHHdJeqnjVtLuS2H2/b9D5aS5+EmJDjfUyXRGWogokk7sN9c7W6mCd\nmkynmqh3sDwO2tC8YdUlO0UvpxMeWVUaMEHCF5LoYQKBgQDcGqzTaRiFCyDRO8Uc\nxrdYPru5gs0YkCkG5dVzkgAVrsniLYKENKLrOjAWJKz4XLGnvYWRgY5Ltp8ovvtv\nKTXixTVPClZ2QmTm+5mIqnZ/vtOSgBcgelFYmw0zuWhufVUb8iT+fooCwPmOsw19\nemZkPbo96L1wy5LTwWOOPFbQbwKBgQDYcs5/5Pkd0kvZiK+JcrJFyU+CD85YsUAN\nca7khzojQQ5bPeurOmAuY94UHrWGail5iJUEHvSk8wDgkKQoQs5CV3+dr+C0Iqx6\negLetiPDwGIUzVF+/Jf4P4u22vMMiEhmk/IcwI9G13P7CgbNHiQZvjaJGpLNcbxt\nl0s1KIS3/QKBgFzRbvJUTn/EeplhoDULY8P16IpJq53hJTwAbiwndJuwMviLgo+n\n9tBFoIOmAb9Wr6ByHsKGpPAu2h1/tF5jPZMc4OctD9sdEpoJnexxHjmuyl/sXlRW\n4LkB4eZfGLgHaH25dnpP+HlC0bqorVat6EH7ee+jl0fawVdFJWuU7HNHAoGBAKbm\nyDK4dhu3uEMyceDzr2G+nG93Dq83ZmO3gJu5Zmwe0xoqQhpTtiyvV2R+VY0jOX38\ngqOd1xmGQ+vlvJ9K/E8Nt1r5brSYdBUxFhtzqVpdc4QE2k2oKusC3RIP/RBx2ho3\nBJ+FIDYJFubB0YLDNiUfll/cPMzsYdbDrft8lfJlAoGAKGG2NLp5tG1gHgpjMpuT\njzQ1wJDJNGSDz0vvOLSETAnjV2YTJQiUqtPYjnR2r0lcWpH3n4JYqPno4umIBWUM\n0wS8YtmpWrcWjuX0YApS/cpIVcLa1ERJ7CiUw2qUPLCOaXAKk/rv5DQ7ytYArnRH\n/igrqpih0DxD5lEk/pc4MuY=\n-----END PRIVATE KEY-----\n",
        "client_email": "disease-database@disease-database-407312.iam.gserviceaccount.com",
        "client_id": "118167799132784564317",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/disease-database%40disease-database-407312.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }

    gc = gspread.service_account_from_dict(credentials_dict)

    # Open the Google Sheet using its title
    sheet = gc.open('Database')

    # Get data from the Diseases sheet
    diseases_data = sheet.worksheet('Sheet1').get_all_records()

    # Convert the data to a DataFrame
    diseases_df = pd.DataFrame(diseases_data)

    return diseases_df

# Function to diagnose disease with probability
def diagnose_disease(selected_symptoms, diseases_data):
    matched_diseases = []

    for index, row in diseases_data.iterrows():
        disease_name = row['Diseases']
        disease_symptoms = set(row['Symptoms'].split(', '))
        
        matched_symptoms = set(selected_symptoms).intersection(disease_symptoms)
        num_matched_symptoms = len(matched_symptoms)

        # Calculate the probability of a match
        probability = (num_matched_symptoms / len(disease_symptoms)) * 100

        # Only consider diseases with at least 1 matched symptom
        if num_matched_symptoms > 0:
            matched_diseases.append((disease_name, probability, matched_symptoms))

    # Sort the matched diseases based on the probability in descending order
    matched_diseases.sort(key=lambda x: x[1], reverse=True)

    return matched_diseases

# Function to get precaution measures
def get_precaution_measures(disease, diseases_data):
    precautions = diseases_data[diseases_data['Diseases'] == disease]['Precautions'].values
    return ", ".join(precautions) if precautions else "Precaution measures not available"

# Streamlit app
def main():
    st.title("Disease Diagnosis App")

    # Fetch data from Google Sheets
    diseases_data = get_data_from_sheets()

    # Get unique symptoms from the DataFrame
    all_symptoms = set(symptom for symptoms_list in diseases_data['Symptoms'].str.split(', ') for symptom in symptoms_list)

    # Get symptoms from user input
    symptoms = st.multiselect("Select your symptoms:", sorted(all_symptoms))

    # Diagnose disease
    diagnose_button_key = hash("diagnose_button_key")  # Unique key
    if st.button("Diagnose", key=diagnose_button_key):
        if not symptoms:
            st.warning("Please select at least one symptom.")
        else:
            matched_diseases = diagnose_disease(symptoms, diseases_data)

            # Display diagnosed diseases and precautions
            if matched_diseases:
                st.success("Based on your selected symptoms, potential matching diseases are:")
                for disease, probability, matched_symptoms in matched_diseases:
                    st.subheader(f"{disease} ({probability:.0f}% probability)")
                    st.write("Matched Symptoms:", ", ".join(matched_symptoms))
                    precautions = get_precaution_measures(disease, diseases_data)
                    st.write("Precaution Measures:", precautions)
            else:
                st.info("No specific diseases matched the selected symptoms. If you have concerns, please consult a healthcare professional.")

if __name__ == "__main__":
    main()
