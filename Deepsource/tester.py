import json

# hilight lines:
d = []
d.append(
    {
        "issue_code": "PYL-W0001",
        "issue_text": "sample title 1",
        "position": {"begin": {"line": 4, "column": 0}, "end": {"line": 4, "column": 0}, "filepath": "/Users/sauravsrijan/Library/Application Support/Sublime Text 3/Packages/Deepsource/tester.py",},
    }
)
d.append(
    {
        "issue_code": "PYL-W0002",
        "issue_text": "sample title 2",
        "position": {"begin": {"line": 8, "column": 0}, "end": {"line": 8, "column": 0}, "filepath": "/Users/sauravsrijan/Library/Application Support/Sublime Text 3/Packages/Deepsource/tester.py",},
    }
)
d.append(
    {
        "issue_code": "PYL-W0001",
        "issue_text": "sample title 1",
        "position": {"begin": {"line": 14, "column": 0}, "end": {"line": 14, "column": 0}, "filepath": "/Users/sauravsrijan/Library/Application Support/Sublime Text 3/Packages/Deepsource/tester.py",},
    }
)

print(json.dumps(d))


# This is a dummy file to run the command right now. After getting the CLI up, delete it.
