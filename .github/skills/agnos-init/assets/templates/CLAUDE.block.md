<!-- AGNOS:BEGIN - written by agnos-init, do not edit: call agnos-init again to update -->
## AGNOS process

This project follows the AGNOS process, installed as a plugin.

Before any other action, invoke the skill named `agnos-process` and follow it. Run its START SESSION ACTION only when the user asks to start a session.

- If that skill is not available, stop and tell the user to install the AGNOS plugin.
- Run the commands from this project's root, where `process/` is.
- Where the process asks the user a question, use the `AskUserQuestion` tool.
<!-- AGNOS:END -->
