# Task API Command Log

This document records the checkpoint commands and actual outputs for each stage.

## Stage 0: hello server

Run command:

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Checkpoint command:

```powershell
curl.exe -i http://127.0.0.1:8000/hello
```

Actual output:

```txt
HTTP/1.1 200 OK
date: Tue, 18 Aug 2026 04:18:16 GMT
server: uvicorn
content-length: 29
content-type: application/json

{"message":"Hello, Task API"}
```

Git commands:

```powershell
git add .
git commit -m "Stage 0: hello server"
git push -u origin main
```

## Stage 1: root and health endpoints

Run command:

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Checkpoint command:

```powershell
curl.exe -sS -i http://127.0.0.1:8000/
```

Actual output:

```txt
HTTP/1.1 200 OK
date: Tue, 18 Aug 2026 05:22:43 GMT
server: uvicorn
content-length: 58
content-type: application/json

{"name":"Task API","version":"1.0","endpoints":["/tasks"]}
```

Checkpoint command:

```powershell
curl.exe -sS -i http://127.0.0.1:8000/health
```

Actual output:

```txt
HTTP/1.1 200 OK
date: Tue, 18 Aug 2026 05:22:43 GMT
server: uvicorn
content-length: 15
content-type: application/json

{"status":"ok"}
```

Git commands:

```powershell
git add .
git commit -m "Stage 1: root and health endpoints"
git push
```

## Stage 2: read endpoints with 404

Run command:

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Checkpoint command:

```powershell
curl.exe -sS -i http://127.0.0.1:8000/tasks
```

Actual output:

```txt
HTTP/1.1 200 OK
date: Tue, 18 Aug 2026 18:36:46 GMT
server: uvicorn
content-length: 146
content-type: application/json

[{"id":1,"title":"Buy groceries","done":false},{"id":2,"title":"Read a chapter of a book","done":true},{"id":3,"title":"Review PRs","done":false}]
```

Checkpoint command:

```powershell
curl.exe -sS -i http://127.0.0.1:8000/tasks/2
```

Actual output:

```txt
HTTP/1.1 200 OK
date: Tue, 18 Aug 2026 18:36:46 GMT
server: uvicorn
content-length: 55
content-type: application/json

{"id":2,"title":"Read a chapter of a book","done":true}
```

Checkpoint command:

```powershell
curl.exe -sS -i http://127.0.0.1:8000/tasks/999
```

Actual output:

```txt
HTTP/1.1 404 Not Found
date: Tue, 18 Aug 2026 18:36:47 GMT
server: uvicorn
content-length: 30
content-type: application/json

{"error":"Task 999 not found"}
```

Git commands:

```powershell
git add .
git commit -m "Stage 2: read endpoints with 404"
git push
```

## Stage 3: create with validation

Run command:

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Checkpoint command:

```powershell
curl.exe -sS -i -X POST http://127.0.0.1:8000/tasks -H "Content-Type: application/json" -d '{""title"":""Write tests""}'
```

Actual output:

```txt
HTTP/1.1 201 Created
date: Wed, 19 Aug 2026 11:06:54 GMT
server: uvicorn
content-length: 43
content-type: application/json

{"id":4,"title":"Write tests","done":false}
```

Checkpoint command:

```powershell
curl.exe -sS -i -X POST http://127.0.0.1:8000/tasks -H "Content-Type: application/json" -d '{}'
```

Actual output:

```txt
HTTP/1.1 400 Bad Request
date: Wed, 19 Aug 2026 11:06:54 GMT
server: uvicorn
content-length: 49
content-type: application/json

{"error":"Title is required and cannot be empty"}
```

Checkpoint command:

```powershell
curl.exe -sS -i -X POST http://127.0.0.1:8000/tasks -H "Content-Type: application/json" -d '{""title"":""   ""}'
```

Actual output:

```txt
HTTP/1.1 400 Bad Request
date: Wed, 19 Aug 2026 11:06:54 GMT
server: uvicorn
content-length: 49
content-type: application/json

{"error":"Title is required and cannot be empty"}
```

Git commands:

```powershell
git add .
git commit -m "Stage 3: create with validation"
git push
```

## Stage 4: full CRUD

Port note: this checkpoint used port `8001` because port `8000` was already occupied by an older local Uvicorn process. If port `8000` is free, the same commands work by replacing `8001` with `8000`.

Run command:

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8001
```

Checkpoint command:

```powershell
curl.exe -sS -i -X PUT http://127.0.0.1:8001/tasks/1 -H "Content-Type: application/json" -d '{""title"":""Buy milk"",""done"":true}'
```

Actual output:

```txt
HTTP/1.1 200 OK
date: Wed, 19 Aug 2026 11:18:28 GMT
server: uvicorn
content-length: 39
content-type: application/json

{"id":1,"title":"Buy milk","done":true}
```

Checkpoint command:

```powershell
curl.exe -sS -i -X PUT http://127.0.0.1:8001/tasks/999 -H "Content-Type: application/json" -d '{""title"":""Missing"",""done"":false}'
```

Actual output:

```txt
HTTP/1.1 404 Not Found
date: Wed, 19 Aug 2026 11:18:28 GMT
server: uvicorn
content-length: 30
content-type: application/json

{"error":"Task 999 not found"}
```

Checkpoint command:

```powershell
curl.exe -sS -i -X PUT http://127.0.0.1:8001/tasks/1 -H "Content-Type: application/json" -d '{""title"":""   "",""done"":false}'
```

Actual output:

```txt
HTTP/1.1 400 Bad Request
date: Wed, 19 Aug 2026 11:18:28 GMT
server: uvicorn
content-length: 49
content-type: application/json

{"error":"Title is required and cannot be empty"}
```

Checkpoint command:

```powershell
curl.exe -sS -i -X PUT http://127.0.0.1:8001/tasks/1 -H "Content-Type: application/json" -d '[]'
```

Actual output:

```txt
HTTP/1.1 400 Bad Request
date: Wed, 19 Aug 2026 11:18:28 GMT
server: uvicorn
content-length: 46
content-type: application/json

{"error":"Request body must be a JSON object"}
```

Checkpoint command:

```powershell
curl.exe -sS -i -X DELETE http://127.0.0.1:8001/tasks/2
```

Actual output:

```txt
HTTP/1.1 204 No Content
date: Wed, 19 Aug 2026 11:18:28 GMT
server: uvicorn

```

Checkpoint command:

```powershell
curl.exe -sS -i -X DELETE http://127.0.0.1:8001/tasks/2
```

Actual output:

```txt
HTTP/1.1 404 Not Found
date: Wed, 19 Aug 2026 11:18:28 GMT
server: uvicorn
content-length: 28
content-type: application/json

{"error":"Task 2 not found"}
```

Git commands:

```powershell
git add .
git commit -m "Stage 4: full CRUD"
git push
```

## Stage 5: Swagger UI

Port note: this checkpoint used port `8002` because ports `8000` and `8001` were already occupied by older local Uvicorn processes. If port `8000` is free, the same commands work by replacing `8002` with `8000`.

Run command:

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8002
```

Checkpoint command:

```powershell
curl.exe -sS -i http://127.0.0.1:8002/docs
```

Actual output:

```txt
HTTP/1.1 200 OK
date: Wed, 19 Aug 2026 12:32:45 GMT
server: uvicorn
content-length: 1007
content-type: text/html; charset=utf-8


    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
    <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
    <title>Task API - Swagger UI</title>
    </head>
    <body>
    <div id="swagger-ui">
    </div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
    const ui = SwaggerUIBundle({
        url: '/openapi.json',
    "dom_id": "#swagger-ui",
"layout": "BaseLayout",
"deepLinking": true,
"showExtensions": true,
"showCommonExtensions": true,
oauth2RedirectUrl: window.location.origin + '/docs/oauth2-redirect',
    presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
    })
    </script>
    </body>
    </html>
```

Checkpoint command:

```powershell
curl.exe -sS http://127.0.0.1:8002/openapi.json | python -c "import json, sys; data = json.load(sys.stdin); print(data['info']['title']); print(data['info']['version']); print(','.join(sorted(data['paths'].keys())))"
```

Actual output:

```txt
Task API
1.0
/,/health,/tasks,/tasks/{task_id}
```

Git commands:

```powershell
git add .
git commit -m "Stage 5: Swagger UI"
git push
```
