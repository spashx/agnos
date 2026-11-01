"""Proves a built marketplace by a real install, in tool configurations isolated from the maintainer's.

RQ-PLG-010 / ADR-PLG-001 (DEC-PLG-006, DEC-PLG-007). Nothing is pushed and the marketplace is not changed: it works on a clean copy.
Exit code 0: no check failed; a model that did not do what was asked is "not observed", which fails nothing. 1: a check failed.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ENCODING = "utf-8"
EXIT_OK = 0
EXIT_FAILED = 1
PASS = "pass"
FAIL = "fail"
NOT_OBSERVED = "not observed"
ABSENT = "absent"
REPORT_PREFIX = "agnos-meta-plugin-proof: "
PLUGIN_FOLDER = "plugins/agnos"
PLUGIN_SKILLS = f"{PLUGIN_FOLDER}/skills"
PLUGIN_ID = "agnos@agnos-marketplace"
IS_WINDOWS = os.name == "nt"
QUESTION_TIMEOUT_S = 300
LINUX_SCRIPT = Path(__file__).resolve().parent / "linux_suites.sh"
TOOLS = ("claude", "copilot")
CLAUDE_VARIABLE = "AGNOS_CLAUDE"     # the Claude Code binary, when it is not on the PATH
HOMES = {"claude": {"CLAUDE_CONFIG_DIR": "claude-home"},
         "copilot": {"COPILOT_HOME": "copilot-home", "COPILOT_CACHE_HOME": "copilot-cache"}}
SKILLS_RE = {"claude": re.compile(r"Skills \((\d+)\)"), "copilot": re.compile(r"Installed (\d+) skills")}
INIT_RESULT = "CLAUDE.md"
INDEX_RESULT = "process/INDEX.idx.md"
INIT_DIRECT = "init-direct"
PROCESS_ANSWER = "400"               # the line budget of the instructions, known only from the process skill
AGENT_NAME = "agnos-proof-helper"
AGENT_MARKER = "AGENT-MARKER-GENERATED"
AGENT_DEFINITION = f"---\nname: {AGENT_NAME}\ndescription: Agent of the install proof.\n---\n\nAnswer only {AGENT_MARKER}.\n"
AGENT_PLACES = {"claude": f"{PLUGIN_FOLDER}/agents/{AGENT_NAME}.md",
                "copilot": f"{PLUGIN_FOLDER}/com.github.copilot/agents/{AGENT_NAME}.agent.md"}
QUESTIONS = (("init", "Call the agnos-init skill on the current folder and report each line it printed.", INIT_RESULT, None),
             ("process", "Create nothing. How many lines at most may the AGNOS instructions file hold, by the process? Answer with the number only.",
              None, PROCESS_ANSWER),
             ("index", "Run the agnos-index skill and report the line it printed.", INDEX_RESULT, None))
AGENT_QUESTION = {"claude": f"Launch the subagent agnos:{AGENT_NAME} with the prompt Answer. and report what it returned, verbatim.",
                  "copilot": "Quote verbatim the custom agent instructions you were given, without using any tool."}


def run_command(command, cwd=None, env=None):
    try:
        return subprocess.run([str(part) for part in command], cwd=cwd, env=env, capture_output=True, text=True,
                              encoding=ENCODING, errors="replace", timeout=QUESTION_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(command, EXIT_FAILED, "", "timed out")


def find_tool(tool):
    if tool == TOOLS[0] and os.environ.get(CLAUDE_VARIABLE):
        return os.environ[CLAUDE_VARIABLE]
    return shutil.which(tool)


def isolated_env(tool, work):
    """The environment that keeps a tool's configuration in the work folder."""
    homes = {name: str(work / folder) for name, folder in HOMES[tool].items()}
    return {**os.environ, **homes}


def check(name, status, detail=""):
    return {"check": name, "status": status, "detail": detail}


def clean_copy(marketplace, work):
    """A copy with only what git tracks when it is a repository, as a clone would give."""
    target = work / "clean"
    if (marketplace / ".git").exists():
        subprocess.run(["git", "clone", "-q", str(marketplace), str(target)], check=True, capture_output=True)
    else:
        shutil.copytree(marketplace, target)
    return target


def add_test_agent(copy):
    """AGNOS delivers no agent today: one in each tool's place proves the place."""
    for place in AGENT_PLACES.values():
        path = copy / place
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(AGENT_DEFINITION, encoding=ENCODING, newline="\n")


# ---- install: no model is called ---------------------------------------------------------------------------------
def prove_install(tool, exe, copy, work, run):
    env = isolated_env(tool, work)
    for name in HOMES[tool].values():
        (work / name).mkdir(parents=True, exist_ok=True)
    checks = []
    if tool == TOOLS[0]:
        for label, folder in (("validate-plugin", copy / PLUGIN_FOLDER), ("validate-catalogue", copy)):
            done = run([exe, "plugin", "validate", folder, "--strict"], env=env)
            checks.append(check(label, FAIL if done.returncode else PASS, done.stdout[-300:] if done.returncode else ""))
    added = run([exe, "plugin", "marketplace", "add", copy], env=env)
    checks.append(check("marketplace-add", FAIL if added.returncode else PASS, added.stdout[-300:] if added.returncode else ""))
    installed = run([exe, "plugin", "install", PLUGIN_ID], env=env)
    checks.append(check("install", FAIL if installed.returncode else PASS, installed.stdout[-300:] if installed.returncode else ""))
    listing = run([exe, "plugin", "details", PLUGIN_ID], env=env) if tool == TOOLS[0] else installed
    found = SKILLS_RE[tool].search(listing.stdout or "")
    expected = sum(1 for path in (copy / PLUGIN_SKILLS).iterdir() if path.is_dir())
    counted = int(found.group(1)) if found else None
    checks.append(check("skills", PASS if counted == expected else FAIL, f"{counted} seen, {expected} in the plugin"))
    return checks


# ---- questions: these call the tools' models, and so cost credits ----------------------------------------------------
def ask_command(tool, exe, plugin, question, agent=False):
    """Scripts only: a question never grants every tool, so that the run stays what was asked."""
    if tool == TOOLS[0]:
        return [exe, "-p", question, "--plugin-dir", str(plugin), "--model", "haiku", "--max-turns", "8", "--allowedTools",
                "Skill", "Agent", "Bash(powershell *)", "PowerShell(powershell *)", "Bash(bash *)", "Bash(python *)"]
    command = [exe, "-p", question, "--no-ask-user"]
    if agent:
        return [*command, "--agent", f"agnos:{AGENT_NAME}", "--deny-tool=read", "--deny-tool=shell"]
    return [*command, "--allow-tool=shell(powershell:*)", "--allow-tool=shell(bash:*)", "--allow-tool=shell(python:*)"]


def initialise_directly(project, plugin, run):
    """The script from the installed plugin, so that the next questions have the block whatever the model did."""
    script = Path(plugin) / "skills" / "agnos-init" / "scripts"
    command = (["powershell", "-NoProfile", "-File", script / "init.ps1", "-Target", "."] if IS_WINDOWS
               else ["bash", script / "init.sh", "--target", "."])
    return FAIL if run(command, cwd=project).returncode else PASS


def ask_questions(tool, exe, plugin, project, work, run, initialise=initialise_directly):
    env = isolated_env(tool, work) if tool != TOOLS[0] else None     # Claude Code's sign-in is in the real configuration: --plugin-dir installs nothing there
    checks = []
    for name, question, result, answer in QUESTIONS:
        done = run(ask_command(tool, exe, plugin, question), cwd=project, env=env)
        observed = (project / result).is_file() if result else answer in (done.stdout or "")
        checks.append(check(name, PASS if observed else NOT_OBSERVED, (done.stdout or "")[-300:] if not observed else ""))
        if name == QUESTIONS[0][0] and not observed:
            checks.append(check(INIT_DIRECT, initialise(project, plugin, run)))
    done = run(ask_command(tool, exe, plugin, AGENT_QUESTION[tool], agent=True), cwd=project, env=env)
    observed = AGENT_MARKER in (done.stdout or "")
    checks.append(check("agent", PASS if observed else NOT_OBSERVED, (done.stdout or "")[-300:] if not observed else ""))
    return checks


# ---- Linux -----------------------------------------------------------------------------------------------------------
def wsl_path(path, run):
    return run(["wsl", "wslpath", "-a", str(path).replace("\\", "/")]).stdout.strip()


def linux_command(repo, windows, run):
    if windows:
        return ["wsl", "--", "bash", wsl_path(LINUX_SCRIPT, run), wsl_path(Path(repo).resolve(), run)]
    return ["bash", str(LINUX_SCRIPT), str(Path(repo).resolve())]


def prove_linux(repo, run):
    done = run(linux_command(repo, IS_WINDOWS, run))
    print(done.stdout)
    return check("linux-suites", FAIL if done.returncode else PASS)


# ---- main --------------------------------------------------------------------------------------------------------------
def parse_args(argv):
    parser = argparse.ArgumentParser(prog="plugin_proof.py", description="Proves a built marketplace by a real install, pushing nothing")
    parser.add_argument("--marketplace", required=True, help="the folder written by agnos-meta-release")
    parser.add_argument("--with-models", action="store_true", help="also put questions to the tools' models: this costs credits")
    parser.add_argument("--linux", action="store_true", help="also run the delivered suites on Linux (under WSL on Windows)")
    parser.add_argument("--repo", default=".", help="the repository whose tree the Linux suites run on (default: the current folder)")
    parser.add_argument("--work", help="working folder, kept; default: a temporary one, removed")
    parser.add_argument("--report", help="file to write the results to, as JSON")
    return parser.parse_args(argv)


def prove_tool(tool, exe, copy, work, args, run):
    checks = prove_install(tool, exe, copy, work, run)
    if args.with_models and not [c for c in checks if c["status"] == FAIL]:
        project = work / f"project-{tool}"
        project.mkdir(parents=True, exist_ok=True)
        run(["git", "init", "-q"], cwd=project)
        checks += ask_questions(tool, exe, copy / PLUGIN_FOLDER, project, work, run)
    return checks


def prove(args, work, run, find):
    results = {}
    copy = clean_copy(Path(args.marketplace), work)
    add_test_agent(copy)
    for tool in TOOLS:
        exe = find(tool)
        results[tool] = prove_tool(tool, exe, copy, work, args, run) if exe else [check(tool, ABSENT)]
    if args.linux:
        results["linux"] = [prove_linux(args.repo, run)]
    return results


def main(argv=None, run=run_command, find=find_tool):
    args = parse_args(argv)
    if not Path(args.marketplace).is_dir():
        print(f"{REPORT_PREFIX}no marketplace at {args.marketplace}: build it with agnos-meta-release", file=sys.stderr)
        return EXIT_FAILED
    holder = None
    if args.work:
        work = Path(args.work).resolve()
        work.mkdir(parents=True, exist_ok=True)
    else:
        holder = tempfile.TemporaryDirectory(prefix="agnos-proof-", ignore_cleanup_errors=True)
        work = Path(holder.name)
    try:
        results = prove(args, work, run, find)
    finally:
        if holder:
            holder.cleanup()
    for tool, checks in results.items():
        for item in checks:
            print(f"{REPORT_PREFIX}{tool} {item['check']}: {item['status']}" + (f" ({item['detail'].strip()})" if item["detail"] else ""))
    if args.report:
        Path(args.report).write_text(json.dumps({"checks": results}, indent=2) + "\n", encoding=ENCODING, newline="\n")
    failed = [item for checks in results.values() for item in checks if item["status"] == FAIL]
    return EXIT_FAILED if failed else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
