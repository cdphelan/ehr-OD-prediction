import json
import os

def extract_er_discharges_simplified(directory_path, encounter_class_code="EMER"):
    """
    Extracts data for ER encounters, assuming all 'finished' encounters are discharges alive.
    NOTE the above assumption, which would make any real analysis inaccurate. 
    This simulated dataset doesn't have any fields/object that determine or accurately infer death

    Args:
        directory_path (str): Path to the directory of JSON files.
        encounter_class_code (str, optional): The Encounter class code for ER visits.
                                            Defaults to "EMER".

    Returns:
        list: A list of dictionaries, each representing an ER encounter.
    """

    er_encounters = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    if data.get("resourceType") == "Bundle" and data.get("entry"):
                        for entry in data["entry"]:
                            resource = entry.get("resource")
                            if resource and resource.get("resourceType") == "Encounter" and \
                               resource.get("class", {}).get("code") == encounter_class_code and \
                               resource.get("status") == "finished":  # Only finished encounters

                                er_encounter = {
                                    "encounter_id": resource.get("id"),
                                    "patient_id": resource.get("subject", {}).get("reference").replace("urn:uuid:", "") if resource.get("subject") else None,
                                    "start_time": resource.get("period", {}).get("start"),
                                    "end_time": resource.get("period", {}).get("end")
                                }
                                er_encounters.append(er_encounter)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Error processing {filename}: {e}")

    er_encounters = pd.DataFrame(er_encounters)
    return er_encounters

if __name__ == "__main__":
    directory_path = "../../synthea-master/output/fhir" 
    er_encounters = extract_er_discharges_simplified(directory_path)
    er_encounters.to_csv("../data/er_encounters.csv", index=False)
