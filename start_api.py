#!/usr/bin/env python3
import os
import uvicorn

port = int(os.environ.get("PORT", "10000"))
uvicorn.run("zhouyi.api:api", host="0.0.0.0", port=port, reload=False)
