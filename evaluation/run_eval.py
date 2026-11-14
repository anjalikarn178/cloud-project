import pandas as pd
import time
import httpx
import re

def evaluate():
    mal_df = pd.read_csv("evaluation/dataset/malicious.csv")
    ben_df = pd.read_csv("evaluation/dataset/benign.csv")
    
    results = {"Regex_Only": {"TP":0, "FP":0, "TN":0, "FN":0, "latency":[]},
               "Hybrid_Guardrail": {"TP":0, "FP":0, "TN":0, "FN":0, "latency":[]}}
               
    print("Evaluating Hybrid Guardrail (FastAPI)...")
    for _, row in pd.concat([mal_df, ben_df]).iterrows():
        start = time.time()
        try:
            httpx.post("http://localhost:8000/chat", json={"prompt": row['text'], "role": "Guest"}, timeout=10.0)
            latency = time.time() - start
            if row['label'] == 'benign':
                results["Hybrid_Guardrail"]["TN"] += 1
            else:
                results["Hybrid_Guardrail"]["FN"] += 1
            results["Hybrid_Guardrail"]["latency"].append(latency * 1000)
        except httpx.HTTPStatusError as e:
            latency = time.time() - start
            if e.response.status_code == 403:
                if row['label'] != 'benign':
                    results["Hybrid_Guardrail"]["TP"] += 1
                else:
                    results["Hybrid_Guardrail"]["FP"] += 1
            results["Hybrid_Guardrail"]["latency"].append(latency * 1000)
        except Exception:
            results["Hybrid_Guardrail"]["latency"].append(0)

    print("Evaluating Regex-Only Baseline...")
    regex_pattern = re.compile(r"dan|ignore|unrestricted|AKIA", re.IGNORECASE)
    for _, row in pd.concat([mal_df, ben_df]).iterrows():
        start = time.time()
        blocked = bool(regex_pattern.search(row['text']))
        latency = time.time() - start
        
        if blocked:
            if row['label'] != 'benign': results["Regex_Only"]["TP"] += 1
            else: results["Regex_Only"]["FP"] += 1
        else:
            if row['label'] == 'benign': results["Regex_Only"]["TN"] += 1
            else: results["Regex_Only"]["FN"] += 1
        results["Regex_Only"]["latency"].append(latency * 1000)

    print("\n--- EVALUATION REPORT ---")
    for name, res in results.items():
        acc = (res["TP"] + res["TN"]) / (res["TP"] + res["TN"] + res["FP"] + res["FN"])
        avg_lat = sum(res["latency"]) / len(res["latency"]) if res["latency"] else 0
        print(f"{name}: Accuracy={acc:.2%} | Avg Latency={avg_lat:.2f}ms | TP={res['TP']} FP={res['FP']} FN={res['FN']}")

if __name__ == "__main__":
    evaluate()