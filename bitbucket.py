import os
import sys
import json
from atlassian import Bitbucket


def gather_data(bitbucket: Bitbucket, project_key: str, repo_slug: str):
    """
    Fetch tag metadata from Bitbucket and return:
    [
      {"tag": "<tag name>", "commit": "<commit hash>"},
      ...
    ]
    """
    tags_resp = bitbucket.get_tags(project_key, repo_slug)

    # Bitbucket DC commonly returns {"values": [...]} for list endpoints
    tag_items = tags_resp.get("values", []) if isinstance(tags_resp, dict) else tags_resp

    results = []
    for t in tag_items:
        tag_name = t.get("displayId") or t.get("id") or t.get("name")

        commit_hash = (
            t.get("latestCommit")
            or t.get("latestChangeset")
            or (t.get("target", {}) or {}).get("hash")
        )

        results.append({"tag": tag_name, "commit": commit_hash})

    return results


def main():
    bitbucket = Bitbucket(
        url="https://bitbucket.fis.dev",
        #username=os.getenv("BITBUCKET_USER"),
        #password=os.getenv("BITBUCKET_PASS"),
        username = "svcacct-swgov-cicd",
        password = "BBDC-NjcyMTEzMjMzMzIyOiuakTRD/0olka2mYBCcAXqga3GB"
    )

    data = gather_data(bitbucket, "OPACICD", "training")
    print(json.dumps(data, indent=2))  # required by Exercise 1
    return 0


if __name__ == "__main__":
    sys.exit(main())