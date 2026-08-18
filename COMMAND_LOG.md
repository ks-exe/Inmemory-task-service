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
