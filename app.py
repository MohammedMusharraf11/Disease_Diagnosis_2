import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials


st.set_page_config(page_title="Disease Diagnosis", page_icon="🏥", layout="centered", initial_sidebar_state="auto", menu_items=None)
# Function to get data from Google Sheets
def get_data_from_sheets():
    # Set up credentials
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
    gc = gspread.authorize(credentials)

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
                    st.write("Precaution Measures:")
                    for precaution in precautions.split(', '):
                        st.write(f"- {precaution}")
            else:
                st.info("No specific diseases matched the selected symptoms. If you have concerns, please consult a healthcare professional.")

if __name__ == "__main__":
    main()
