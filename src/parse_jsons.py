import os
import json
import pandas as pd
from datetime import datetime


def extract_patient_data(directory_path):
    """
    Extracts patient data from FHIR JSON files in a directory.

    Args:
        directory_path (str): The path to the directory containing the JSON files.

    Returns:
        list: A list of dictionaries, where each dictionary represents a patient
              and contains the extracted data.
    """
    patient_data_list = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    #print(data) #for debugging
                    # Check if it is a Bundle and has entries
                    if data.get("resourceType") == "Bundle" and data.get("entry"):
                        for entry in data["entry"]:
                            # Check if the entry is a Patient resource
                            if entry.get("resource", {}).get("resourceType") == "Patient":
                                patient_resource = entry["resource"]

                                # Extract the required data, handling potential missing fields
                                patient_id = patient_resource.get("id")
                                #patient_id = patient_resource.get("identifier")[0].get("value") #original
                                race_display = ""
                                ethnicity_display = ""
                                
                                for ext in patient_resource.get("extension", []):
                                    if ext.get("url") == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race":
                                        for race_ext in ext.get("extension", []):
                                            if race_ext.get("url") == "text":
                                                race_display = race_ext.get("valueString", "")
                                    elif ext.get("url") == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity":
                                        for ethnicity_ext in ext.get("extension", []):
                                            if ethnicity_ext.get("url") == "text":
                                                ethnicity_display = ethnicity_ext.get("valueString", "")

                                birth_sex = None  # Initialize to None in case the extension is not found
                                for ext in patient_resource.get("extension", []):
                                    if ext.get("url") == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex":
                                        birth_sex = ext.get("valueCode")

                                gender = patient_resource.get("gender")
                                birth_date = patient_resource.get("birthDate")
                                address_data = patient_resource.get("address", [{}])[0]  # Get the first address, if available
                                address = {
                                    "street": address_data.get("line", [""])[0],  # Get the first line
                                    "city": address_data.get("city"),
                                    "state": address_data.get("state"),
                                    "postalCode": address_data.get("postalCode"),
                                    "country": address_data.get("country"),
                                }
                                marital_status = patient_resource.get("maritalStatus", {}).get("text")

                                patient_data = {
                                    "id": patient_id,
                                    "race_display": race_display,
                                    "ethnicity_display": ethnicity_display,
                                    "birth_sex": birth_sex,
                                    "gender": gender,
                                    "birth_date": birth_date,
                                    "address": address,
                                    "marital_status": marital_status,
                                }
                                patient_data_list.append(patient_data)
                    else:
                        print(f"Skipping file: {filename} - Not a FHIR Bundle or empty")

            except json.JSONDecodeError:
                print(f"Error decoding JSON from file: {filename}")
            except Exception as e:
                print(f"An error occurred while processing file {filename}: {e}")
    patient_data_list = pd.DataFrame(patient_data_list)
    return patient_data_list


def extract_encounter_data(directory_path):
    """
    Extracts encounter data from FHIR JSON files in a directory.

    Args:
        directory_path (str): The path to the directory containing the JSON files.

    Returns:
        list: A list of dictionaries, where each dictionary represents an encounter
              and contains the extracted data.
    """
    encounter_data_list = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    # Check if it is a Bundle and has entries
                    if data.get("resourceType") == "Bundle" and data.get("entry"):
                        for entry in data["entry"]:
                            # Check if the entry is an Encounter resource
                            if entry.get("resource", {}).get("resourceType") == "Encounter":
                                encounter_resource = entry["resource"]

                                # Extract the required data, handling potential missing fields
                                encounter_id = encounter_resource.get("id")
                                subject_reference = encounter_resource.get("subject", {}).get("reference") #changed
                                patient_id = subject_reference.replace("urn:uuid:", "") if subject_reference else None

                                
                                type_code = None
                                type_display = None
                                if encounter_resource.get("type"): #added this check
                                  for t in encounter_resource["type"]: #and this loop
                                    for c in t.get("coding", []):
                                        type_code = c.get("code")
                                        type_display = c.get("display")
                                        break # added break to exit loop after first code is found
                                
                                start_time = encounter_resource.get("period", {}).get("start")
                                end_time = encounter_resource.get("period", {}).get("end")
                                class_code = encounter_resource.get("class", {}).get("code")
                                #status = encounter_resource.get("status") #all are "finished" so no information

                                encounter_data = {
                                    "encounter_id": encounter_id,
                                    "patient_id": patient_id,
                                    "type_code": type_code,
                                    "type_display": type_display,
                                    "start_time": start_time,
                                    "end_time": end_time,
                                    "class_code": class_code,
                                }
                                encounter_data_list.append(encounter_data)
                    else:
                        print(f"Skipping file: {filename} - Not a FHIR Bundle or empty")

            except json.JSONDecodeError:
                print(f"Error decoding JSON from file: {filename}")
            except Exception as e:
                print(f"An error occurred while processing file {filename}: {e}")
   
    encounter_data_list = pd.DataFrame(encounter_data_list)
    return encounter_data_list


def extract_condition_data(directory_path):
    """
    Extracts condition data from FHIR JSON files in a directory.

    Args:
        directory_path (str): The path to the directory containing the JSON files.

    Returns:
        list: A list of dictionaries, where each dictionary represents a condition
              and contains the extracted data.
    """
    condition_data_list = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    # Check if it is a Bundle and has entries
                    if data.get("resourceType") == "Bundle" and data.get("entry"):
                        for entry in data["entry"]:
                            # Check if the entry is a Condition resource
                            if entry.get("resource", {}).get("resourceType") == "Condition":
                                condition_resource = entry["resource"]

                                # Extract the required data, handling potential missing fields
                                condition_id = condition_resource.get("id")

                                # Extract patient reference and remove "urn:uuid:" prefix
                                patient_reference = condition_resource.get("subject", {}).get("reference")
                                patient_id = patient_reference.replace("urn:uuid:", "") if patient_reference else None

                                # Extract encounter reference and remove "urn:uuid:" prefix
                                encounter_reference = condition_resource.get("encounter", {}).get("reference")
                                encounter_id = encounter_reference.replace("urn:uuid:", "") if encounter_reference else None

                                # Extract code information
                                code_data = condition_resource.get("code", {})
                                code_coding = code_data.get("coding", [])
                                #code system is SNOMED CT
                                #code_system = code_coding[0].get("system") if code_coding else None
                                code_value = code_coding[0].get("code") if code_coding else None
                                code_text = code_data.get("text")

                                # Extract date/time values, converting to datetime objects
                                onset_date = condition_resource.get("onsetDateTime")
                                onset_datetime = datetime.fromisoformat(onset_date) if onset_date else None

                                abatement_date = condition_resource.get("abatementDateTime")
                                abatement_datetime = datetime.fromisoformat(abatement_date) if abatement_date else None

                                recorded_date = condition_resource.get("recordedDate")
                                recorded_datetime = datetime.fromisoformat(recorded_date) if recorded_date else None

                                condition_data = {
                                    "condition_id": condition_id,
                                    "patient_id": patient_id,
                                    "encounter_id": encounter_id,
                                    "code_value": code_value,
                                    "code_text": code_text,
                                    "onset_datetime": onset_datetime,
                                    "abatement_datetime": abatement_datetime,
                                    "recorded_datetime": recorded_datetime,
                                }
                                condition_data_list.append(condition_data)
                    else:
                        print(f"Skipping file: {filename} - Not a FHIR Bundle or empty")

            except json.JSONDecodeError:
                print(f"Error decoding JSON from file: {filename}")
            except ValueError as ve:
                print(f"ValueError processing file {filename}: {ve}")
            except Exception as e:
                print(f"An error occurred while processing file {filename}: {e}")
    
    condition_data_list = pd.DataFrame(condition_data_list)
    return condition_data_list

if __name__ == "__main__":
    directory_path = "../../synthea-master/output/fhir" 
    patients_df = extract_patient_data(directory_path)
    patients_df.to_csv("../data/patients.csv", index=False)

    condition_df = extract_condition_data(directory_path)
    condition_df.to_csv("../data/conditions.csv", index=False)

    encounter_df = extract_encounter_data(directory_path)
    encounter_df.to_csv("../data/encounters.csv", index=False)





