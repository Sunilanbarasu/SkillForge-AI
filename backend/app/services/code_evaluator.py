import subprocess
import sys
import tempfile
import json
from pathlib import Path

TIMEOUT_SECONDS = 5


def evaluate_python_code(code: str, test_cases: list) -> dict:
    if not code or not code.strip():
        return {
            "passed": False,
            "score": 0.0,
            "passed_tests": 0,
            "total_tests": len(test_cases or []),
            "feedback": "No code was submitted."
        }

    if not test_cases:
        return {
            "passed": False,
            "score": 0.0,
            "passed_tests": 0,
            "total_tests": 0,
            "feedback": "No test cases configured."
        }

    forbidden = [
        "import os",
        "import subprocess",
        "import shutil",
        "import socket",
        "import requests",
        "import urllib",
        "from os",
        "from subprocess",
        "from socket",
        "__import__",
        "eval(",
        "exec(",
        "open(",
        "system(",
        "popen("
    ]

    lowered = code.lower()

    for pattern in forbidden:
        if pattern in lowered:
            return {
                "passed": False,
                "score": 0.0,
                "passed_tests": 0,
                "total_tests": len(test_cases),
                "feedback": "Restricted operation detected: " + pattern
            }

    with tempfile.TemporaryDirectory(prefix="skillforge_eval_") as temp_dir:
        temp = Path(temp_dir)

        solution_file = temp / "solution.py"
        runner_file = temp / "runner.py"

        solution_file.write_text(code, encoding="utf-8")

        runner_code = """import json
import sys

solution_path = sys.argv[1]
test_json = sys.argv[2]

try:
    tests = json.loads(test_json)
except Exception as exc:
    print(json.dumps({
        "passed_tests": 0,
        "total_tests": 0,
        "score": 0.0,
        "failures": [
            "Test configuration error: "
            + type(exc).__name__
            + ": "
            + str(exc)
        ]
    }))
    raise SystemExit(0)

namespace = {
    "__builtins__": {
        "abs": abs,
        "all": all,
        "any": any,
        "bool": bool,
        "dict": dict,
        "enumerate": enumerate,
        "filter": filter,
        "float": float,
        "int": int,
        "len": len,
        "list": list,
        "map": map,
        "max": max,
        "min": min,
        "range": range,
        "reversed": reversed,
        "round": round,
        "set": set,
        "sorted": sorted,
        "str": str,
        "sum": sum,
        "tuple": tuple,
        "zip": zip
    }
}

try:
    source = open(solution_path, "r", encoding="utf-8").read()
    compiled = compile(source, solution_path, "exec")
    exec(compiled, namespace)

except SyntaxError as exc:
    print(json.dumps({
        "passed_tests": 0,
        "total_tests": len(tests),
        "score": 0.0,
        "failures": [
            "SyntaxError: "
            + str(exc)
        ]
    }))
    raise SystemExit(0)

except Exception as exc:
    print(json.dumps({
        "passed_tests": 0,
        "total_tests": len(tests),
        "score": 0.0,
        "failures": [
            type(exc).__name__
            + ": "
            + str(exc)
        ]
    }))
    raise SystemExit(0)

passed = 0
failures = []

for index, test in enumerate(tests, 1):
    function_name = test.get("function", "solution")
    function = namespace.get(function_name)

    if not callable(function):
        failures.append(
            "Test "
            + str(index)
            + ": function '"
            + function_name
            + "' not found."
        )
        continue

    raw_input = test.get("input")

    try:
        if isinstance(raw_input, list):
            actual = function(*raw_input)
        elif isinstance(raw_input, dict):
            actual = function(**raw_input)
        else:
            actual = function(raw_input)

        expected = test.get("expected_output")

        if actual == expected:
            passed += 1
        else:
            failures.append(
                "Test "
                + str(index)
                + ": Wrong Answer — expected "
                + repr(expected)
                + ", got "
                + repr(actual)
                + "."
            )

    except Exception as exc:
        failures.append(
            "Test "
            + str(index)
            + ": Runtime Error — "
            + type(exc).__name__
            + ": "
            + str(exc)
        )

total = len(tests)
score = round((passed / total) * 100, 2) if total else 0.0

print(json.dumps({
    "passed_tests": passed,
    "total_tests": total,
    "score": score,
    "failures": failures
}))
"""

        runner_file.write_text(runner_code, encoding="utf-8")

        try:
            process = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    str(runner_file),
                    str(solution_file),
                    json.dumps(test_cases)
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS
            )

        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "score": 0.0,
                "passed_tests": 0,
                "total_tests": len(test_cases),
                "feedback": "Execution timed out after 5 seconds."
            }

        output = process.stdout.strip()

        if not output:
            return {
                "passed": False,
                "score": 0.0,
                "passed_tests": 0,
                "total_tests": len(test_cases),
                "feedback": process.stderr.strip()[-2000:] or "Execution failed."
            }

        try:
            result = json.loads(output.splitlines()[-1])

        except Exception:
            return {
                "passed": False,
                "score": 0.0,
                "passed_tests": 0,
                "total_tests": len(test_cases),
                "feedback": "Evaluator returned an invalid result."
            }

        passed_tests = int(result.get("passed_tests", 0))
        total_tests = int(result.get("total_tests", len(test_cases)))
        score = float(result.get("score", 0.0))
        failures = result.get("failures", [])

        return {
            "passed": passed_tests == total_tests and total_tests > 0,
            "score": score,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "feedback": (
                "All test cases passed."
                if passed_tests == total_tests
                else "\n".join(failures[:5]) or "Some tests failed."
            )
        }
