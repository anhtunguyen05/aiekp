import urllib.parse
import urllib.request
import json

node_id = r"D:\AIEKP\plugins\python_parser\tests\test_parser.py::test_python_parser"
encoded_id = urllib.parse.quote(node_id, safe="")
url = f"http://localhost:8000/graph/nodes/{encoded_id}"
print(f"Requesting: {url}")
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        print("Success:", json.dumps(data, indent=2))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code, e.read().decode())
except Exception as e:
    print("Error:", e)
