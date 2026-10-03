#!/usr/bin/env python3
import os

if __name__ == "__main__":
    if os.getenv("GITHUB_ACTIONS") == "true":
        from workflow.run import main as workflow_main
        workflow_main()
    else:
        from local.run import main as local_main
        local_main()
