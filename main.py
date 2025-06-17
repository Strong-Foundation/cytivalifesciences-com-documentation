import http.client
import json

conn = http.client.HTTPSConnection(host="api.cytivalifesciences.com")
payload: str = json.dumps(
    obj={"query": "", "pageSize": 5000, "currentPage": 1, "filters": [], "sorting": ""}
)
headers: dict[str, str] = {
    "Content-Type": "application/json",
}
conn.request(
    method="POST", url="/ap-doc-search/v1/sds-document", body=payload, headers=headers
)
res: http.client.HTTPResponse = conn.getresponse()
data: bytes = res.read()
print(data.decode(encoding="utf-8"))
