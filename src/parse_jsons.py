import os
import json
import pandas as pd
from datetime import datetime

def parse_fhir_bundle(filepath):
    with open(filepath, 'r') as f:
        bundle = json.load(f)
    
    patient_info = {}
    conditions = []
    medications = []

    for entry in bundle.get('entry', []):
        resource = entry.get('resource', {})
        resource_type = resource.get('resourceType')

        if resource_type == 'Patient':
            patient_info['patient_id'] = resource.get('id')
            patient_info['birthDate'] = resource.get('birthDate')
            patient_info['gender'] = resource.get('gender')

        elif resource_type == 'Condition':
            condition_text = resource.get('code', {}).get('text')
            if condition_text:
                conditions.append(condition_text)

        elif resource_type == 'MedicationRequest':
            med_text = resource.get('medicationCodeableConcept', {}).get('text')
            if med_text:
                medications.append(med_text)

    return patient_info, conditions, medications

def parse_folder(folder_path):
    patient_records = []
    condition_records = []
    medication_records = []

    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            filepath = os.path.join(folder_path, filename)
            patient_info, conditions, medications = parse_fhir_bundle(filepath)
            
            if patient_info:
                patient_records.append(patient_info)
                for cond in conditions:
                    condition_records.append({'patient_id': patient_info['patient_id'], 'condition': cond})
                for med in medications:
                    medication_records.append({'patient_id': patient_info['patient_id'], 'medication': med})

    patients_df = pd.DataFrame(patient_records)
    conditions_df = pd.DataFrame(condition_records)
    medications_df = pd.DataFrame(medication_records)

    return patients_df, conditions_df, medications_df

if __name__ == "__main__":
    patients_df, conditions_df, medications_df = parse_folder("path/to/your/json/folder")

    # Save processed CSVs
    patients_df.to_csv("../data/processed/patients.csv", index=False)
    conditions_df.to_csv("../data/processed/conditions.csv", index=False)
    medications_df.to_csv("../data/processed/medications.csv", index=False)

    print("Parsing complete! Data saved to processed folder.")
