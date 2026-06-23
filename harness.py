import requests
import json
import urllib3
from urllib.parse import unquote

urllib3.disable_warnings()

HARNESS_API_KEY = "sat.XzgUIuZXRMWymCzLKYZpCg.6988fb36d80a3d4186e7f3b6.mVF41xiSGWfFRkezbISa"
ACCOUNT_ID = "XzgUIuZXRMWymCzLKYZpCg"
ORG_ID = "NorthStar_PoC"
PROJECT_ID = "Ramp_Up_Training"
PIPELINE_ID = "SamplePipeline"

# ✔ Correct endpoint for listing executions
BASE_URL = "https://app.harness.io/pipeline/api/pipelines/execution/summary/outline"

session = requests.Session()
session.verify = False
session.trust_env = False
session.headers.update({
    "x-api-key": HARNESS_API_KEY,
    "Accept": "application/json"
})

def gather_data():
    params = {
        "accountIdentifier": ACCOUNT_ID,
        "orgIdentifier": ORG_ID,
        "projectIdentifier": PROJECT_ID,
        "pipelineIdentifier": PIPELINE_ID,
        "page": 0,
        "size": 50
    }

    r = session.post(BASE_URL, params=params, timeout=30)

    print("DEBUG RAW:", unquote(r.request.url))

    if r.status_code != 200:
        raise RuntimeError(f"Failed (HTTP {r.status_code}): {r.text}")

    entries = r.json().get("data", {}).get("content", [])

    output = []
    for e in entries:
        output.append({
            "planExecutionId": e.get("planExecutionId"),
            "status": e.get("status"),
            "startTs": e.get("startTs"),
            "endTs": e.get("endTs")
        })
    return output

def main():
    print(json.dumps(gather_data(), indent=2))

if __name__ == "__main__":
    main()