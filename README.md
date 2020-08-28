## DeepSource Sublime Plugin.

This Is a SublimeText 3 plugin developed to support local runs on deepsource.
It calls the `cli` with the flag `--analyze` for a single `filepath` and uses the result sent by cli to raise issues.

It enables these keyboard shortcuts (Right now, support is only for mac)
- `cmd+option+a` : Run DepSource Analysis on the filepath opened in the editor.
- `cmd+option+q` : Adds a `# skipcq: <issue_code>` to the line where a DeepSource issue is raised.

Steps to enable this plugin in your IDE:
run: `make install-plugin` from the repo root.
Prerequisite: Sublime text must be installed, otherwise this command will fail.

NOTE: Make sure the DeepSource CLI is installed too.
