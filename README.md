# Introduction

This is a simple GET supporting Web Proxy Server with caching support. Proxy
Server is coded in Python 3 and serves on port 12345. It also supports caching
of up to 3 responses.

It also logs all the activity being performed by it on the screen.

For caching, it first checks if the file on the server has been modified or not
and then requests for the whole file if not already done so.

## Directory Structure

```
.
├── file_server
│   ├── 1.txt
│   ├── 2.binary
│   └── server.py
├── proxy_server
│   ├── config.py
│   └── proxy_server.py
└── README.md
```

## How to Run

From root directory:

```
python3 proxy_server/proxy_server.py
```
