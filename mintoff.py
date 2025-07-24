import json
from collections import Counter
import pandas as pd
import os

class DisputeParser:
    def __init__(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.rounds = self.data.get("rounds", [])
        self.filepath = filepath

    def get_metadata(self):
        return {
            "dispute_id": self.data.get("id"),
            "current_ruling": self.data.get("currentRulling"),
            "start_time": self.data.get("startTime")
        }

    def get_final_round_summary(self):
        if not self.rounds:
            return None
        final_round = self.rounds[-1]
        choices = [v["choice"] for v in final_round["votes"] if v.get("voted") and v.get("choice") in ("1", "2")]
        count = Counter(choices)
        total = count["1"] + count["2"]
        if total == 0:
            return None

        majority = "1" if count["1"] > count["2"] else "2"
        minority = "2" if majority == "1" else "1"
        x_votes = count[majority]
        y_votes = count[minority]
        x_pct = round(100 * x_votes / total, 2)
        y_pct = round(100 * y_votes / total, 2)

        return {
            "X_votes": x_votes,
            "Y_votes": y_votes,
            "X_percent": x_pct,
            "Y_percent": y_pct,
            "X_is": "Yes" if majority == "2" else "No",
            "majority_choice": majority,
            "total_votes": total
        }

    def interpret_choices(self):
        ruling = self.data.get("currentRulling")
        return {
            "choice_1": "No",
            "choice_2": "Yes",
            "final_ruling": "Yes" if ruling == "2" else "No"
        }

    def print_summary(self):
        meta = self.get_metadata()
        final = self.get_final_round_summary()
        interp = self.interpret_choices()

        print("*" * 50)
        print(f"DISPUTE NUMBER: {meta['dispute_id']}")
        print(f"FINAL DECISION: {interp['final_ruling']}")
        print("*" * 50)
        print(f"X = {final['X_votes']} out of {final['total_votes']} votes - {final['X_percent']}%")
        print(f"Y = {final['Y_votes']} out of {final['total_votes']} votes - {final['Y_percent']}%\n")
        print(f"IN THIS CASE, X was {final['X_is'].upper()}")
        print("*" * 50)

    def export_final_round_to_excel(self, output_path=None):
        final = self.get_final_round_summary()
        if not final:
            print("[!] No votes to export.")
            return

        df = pd.DataFrame({
            "Vote Count": [final["X_votes"], final["Y_votes"]],
            "Total Jurors": [final["total_votes"], final["total_votes"]],
            "Ratio": [round(final["X_percent"] / 100, 2), round(final["Y_percent"] / 100, 2)]
        }, index=["X", "Y"])

        dispute_id = self.get_metadata()["dispute_id"]
        if output_path is None:
            output_path = f"dispute{dispute_id}.csv"

        df.to_csv(output_path)

        print("\n" + "-" * 50)
        print("[!] FILE SAVED SUCCESSFULLY".center(50))
        print("-" * 50)
        print(f"CSV file saved to: {output_path}\n")

        print(f"How much would you like to tip to Gabriel? [£100] [£500] [£1000] [£5000]")



# === USER INPUT + EXECUTION ===

# Prompt for file name
filename_input = input("[!] Enter dispute file name (without .json): ").strip()
base_path = r"C:\Users\Satyam\OneDrive\Desktop\Satyam\Master's Thesis\python code\Kleros 2.0"
filepath = os.path.join(base_path, f"{filename_input}.json")

# Run
try:
    parser = DisputeParser(filepath)
    parser.print_summary()
    parser.export_final_round_to_excel()
except FileNotFoundError:
    print("\n" + "-" * 50)
    print("[!] ERROR: FILE NOT FOUND".center(50))
    print("-" * 50)
    print(f"Could not find file: {filepath}")
except Exception as e:
    print("\n" + "-" * 50)
    print("[!] ERROR OCCURRED".center(50))
    print("-" * 50)
    print(str(e))
