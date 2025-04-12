
import os
import uuid
import time
import json
import logging
import shutil
import tempfile
import docker
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)


class CodeExecutor:
    """
    A language-agnostic code executor that creates a temporary program to wrap user
    submissions. For Python, this wrapper expects a class named 'Solution' that can have
    any method name (for example, 'twoSum', 'reverse', etc.). The wrapper:
      1. Reads STDIN as a string representing the test input.
      2. Tries to parse that string first as JSON, then as a Python literal.
      3. Instantiates the `Solution` class.
      4. Dynamically discovers the first non-dunder callable method on the instance.
      5. Calls the discovered method with the parsed arguments.
      6. Prints the marker "OUTPUT_START" followed by the result.
    
    Similar wrappers for Java, JavaScript, and C++ are provided as examples.
    """

    SUPPORTED_LANGUAGES = {
        'python': {
            'image': 'python:3.10-alpine',
            'file_extension': '.py',
            # No extra setup is needed.
            'setup': lambda dir_path: None,
            # Pipe the test input from /app/input.txt into the python process.
            'run_command': lambda file_path: f"sh -c \"cat /app/input.txt | python {file_path}\""
        },
        'javascript': {
            'image': 'node:14-alpine',
            'file_extension': '.js',
            'setup': lambda dir_path: None,
            'run_command': lambda file_path: f"sh -c \"cat /app/input.txt | node {file_path}\""
        },
        'java': {
            'image': 'openjdk:11-jdk-slim',
            'file_extension': '.java',
            'setup': lambda dir_path: CodeExecutor._setup_java(dir_path),
            'run_command': lambda file_path: (
                f"sh -c \"javac {file_path} && cat /app/input.txt | java -cp /app Solution\""
            )
        },
        'cpp': {
            'image': 'gcc:latest',
            'file_extension': '.cpp',
            'setup': lambda dir_path: None,
            'run_command': lambda file_path: (
                f"sh -c \"g++ -o /app/solution {file_path} && cat /app/input.txt | /app/solution\""
            )
        }
    }

    def __init__(self):
        self.logger = app.logger
        self.logger.debug("Initializing Docker client for CodeExecutor")
        try:
            self.client = docker.from_env()
        except Exception as e:
            self.logger.exception("Failed to initialize Docker client")
            raise e

    @staticmethod
    def _setup_java(dir_path):
        """
        Java-specific setup if needed.
        """
        app.logger.debug(f"Setting up Java environment in {dir_path}")
        # No additional steps required by default.
        return

    def execute_code(self, code, language, test_cases):
        """
        Run the user-submitted code against each test case. Each test case is run in its own
        temporary folder and Docker container.
        """
        self.logger.debug(f"Executing code with language: {language}")

        if language not in self.SUPPORTED_LANGUAGES:
            err_msg = f"Language '{language}' is not supported."
            self.logger.error(err_msg)
            return {'status': 'error', 'message': err_msg}

        lang_conf = self.SUPPORTED_LANGUAGES[language]
        test_results = []
        start_time = time.time()

        for idx, test_case in enumerate(test_cases):
            # Extract input and expected output from the test case.
            input_data = test_case.get('test_case') or test_case.get('input')
            expected = test_case.get('expected')
            self.logger.debug(f"Processing test case {idx + 1}: input: {input_data}")

            # Create an isolated temporary directory for this test execution.
            temp_dir = tempfile.mkdtemp(prefix="leetcode-execution-")
            try:
                # Create the full test program with our test runner wrapper.
                program = self._create_test_program(code, language)
                file_name = f"solution{lang_conf['file_extension']}"
                file_path = os.path.join(temp_dir, file_name)
                with open(file_path, 'w') as f:
                    f.write(program)

                # Write the test input to input.txt.
                input_file = os.path.join(temp_dir, "input.txt")
                with open(input_file, 'w') as f:
                    f.write(input_data)

                # Set file permissions to ensure Docker can read them.
                os.chmod(temp_dir, 0o755)
                os.chmod(file_path, 0o644)
                os.chmod(input_file, 0o644)

                # Run language-specific setup if needed.
                setup_fn = lang_conf.get('setup')
                if setup_fn:
                    setup_fn(temp_dir)

                container_file_path = os.path.join("/app", file_name)
                command = lang_conf['run_command'](container_file_path)
                self.logger.debug(f"Running container with command: {command}")

                container = self.client.containers.run(
                    image=lang_conf['image'],
                    command=command,
                    volumes={os.path.abspath(temp_dir): {"bind": "/app", "mode": "rw"}},
                    detach=True,
                    stdout=True,
                    stderr=True,
                    mem_limit='128m',
                    network_disabled=True
                )

                try:
                    result = container.wait(timeout=5)
                except Exception:
                    self.logger.exception("Container execution timed out.")
                    test_results.append({
                        'test_case': input_data,
                        'expected': expected,
                        'actual': "Time Limit Exceeded",
                        'passed': False
                    })
                    container.remove(force=True)
                    continue

                logs = container.logs().decode('utf-8').strip()
                exit_code = result.get('StatusCode', 1)

                if exit_code != 0:
                    test_results.append({
                        'test_case': input_data,
                        'expected': expected,
                        'actual': f"Runtime Error: {logs}",
                        'passed': False
                    })
                else:
                    # Look for output printed after the marker.
                    actual_output = self._extract_output(logs)
                    passed = self._compare_output(actual_output, expected)
                    test_results.append({
                        'test_case': input_data,
                        'expected': expected,
                        'actual': actual_output,
                        'passed': passed
                    })
                container.remove(force=True)
            except Exception as e:
                self.logger.exception("Error during test case execution")
                test_results.append({
                    'test_case': input_data,
                    'expected': expected,
                    'actual': f"Execution Error: {str(e)}",
                    'passed': False
                })
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)

        total_time = time.time() - start_time
        overall_status = "accepted" if all(tr.get("passed", False) for tr in test_results) else "wrong_answer"
        summary = {
            'status': overall_status,
            'execution_time': total_time,
            'memory_usage': '128MB',
            'test_results': test_results
        }
        self.logger.debug(f"Execution completed: {summary}")
        return summary

    def _create_test_program(self, user_code, language):
        """
        Build the complete program to be executed in the container. For Python the wrapper:
          - Inserts the user's submission (which defines class Solution)
          - Provides a `run_test()` function that:
             1. Reads STDIN (test input)
             2. Attempts to parse it (first JSON, then with ast.literal_eval)
             3. Instantiates the `Solution` class.
             4. Dynamically selects the first non-dunder callable method.
             5. Invokes that method with the parsed arguments.
             6. Prints the "OUTPUT_START" marker and the function result.
        """
        if language == 'python':
            program = f"""\
# ----- User Code Start -----
{user_code}
# ----- User Code End -----

import sys
import json
import ast
import inspect

def run_test():
    test_input = sys.stdin.read().strip()
    args = None
    # Try parsing as JSON.
    try:
        args = json.loads(test_input)
    except Exception:
        try:
            args = ast.literal_eval(test_input)
        except Exception as parse_ex:
            print("OUTPUT_START")
            print("Error: invalid test input format")
            return
    # Ensure that arguments are given in tuple/list form.
    if not isinstance(args, (list, tuple)):
        args = (args,)
    try:
        sol = Solution()
    except Exception as e:
        print("OUTPUT_START")
        print(f"Error creating Solution instance: {{e}}")
        return
    # Get all callable methods that are not built-in.
    methods = [getattr(sol, attr) for attr in dir(sol) if callable(getattr(sol, attr)) and not attr.startswith("__")]
    if not methods:
        print("OUTPUT_START")
        print("Error: no valid method found in Solution")
        return
    # Select the first candidate. (You might refine this logic per problem in the future.)
    candidate = methods[0]
    try:
        result = candidate(*args)
    except Exception as e:
        result = f"Error executing function: {{e}}"
    print("OUTPUT_START")
    print(result)

if __name__ == '__main__':
    run_test()
"""
            return program
        elif language == 'javascript':
            program = f"""\
// ----- User Code Start -----
{user_code}
// ----- User Code End -----

function runTest() {{
    let inputData = '';
    process.stdin.on('data', function(chunk) {{
        inputData += chunk;
    }});
    process.stdin.on('end', function() {{
        let args;
        try {{
            args = JSON.parse(inputData);
        }} catch (err) {{
            console.log("OUTPUT_START");
            console.log("Error: invalid test input format");
            return;
        }}
        const sol = new Solution();
        const keys = Object.getOwnPropertyNames(Object.getPrototypeOf(sol)).filter(k => k !== 'constructor');
        if (keys.length === 0) {{
            console.log("OUTPUT_START");
            console.log("Error: no valid method found in Solution");
            return;
        }}
        let candidate = sol[keys[0]];
        try {{
            const result = candidate.apply(sol, Array.isArray(args) ? args : [args]);
            console.log("OUTPUT_START");
            console.log(result);
        }} catch (e) {{
            console.log("OUTPUT_START");
            console.log("Error executing function: " + e);
        }}
    }});
}}
runTest();
"""
            return program
        elif language == 'java':
            # For Java, the wrapper assumes that there is a static method (or that reflection is used).
            # For simplicity, we expect a static method `solve` in the submission.
            program = f"""\
// ----- User Code Start -----
public class Solution {{
{user_code}
    public static String solve(String input) {{
        return "";
    }}
    public static void main(String[] args) {{
        try {{
            java.util.Scanner scanner = new java.util.Scanner(System.in);
            String testInput = scanner.useDelimiter("\\\\A").next();
            scanner.close();
            String result = solve(testInput);
            System.out.println("OUTPUT_START");
            System.out.println(result);
        }} catch (Exception e) {{
            System.out.println("OUTPUT_START");
            System.out.println("Error executing solution: " + e.getMessage());
        }}
    }}
}}
// ----- User Code End -----
"""
            return program
        elif language == 'cpp':
            program = f"""\
// ----- User Code Start -----
{user_code}
// ----- User Code End -----

#include <iostream>
#include <sstream>
#include <string>

std::string solve(const std::string &input) {{
    return "";
}}

int main() {{
    std::stringstream buffer;
    buffer << std::cin.rdbuf();
    std::string testInput = buffer.str();
    std::string result;
    try {{
        result = solve(testInput);
    }} catch (...) {{
        result = "Error executing function";
    }}
    std::cout << "OUTPUT_START" << std::endl;
    std::cout << result << std::endl;
    return 0;
}}
"""
            return program
        else:
            return user_code

    @staticmethod
    def _extract_output(logs):
        """
        Extract text following the OUTPUT_START marker from the logs.
        """
        marker = "OUTPUT_START"
        if marker in logs:
            parts = logs.split(marker, 1)
            return parts[1].strip()
        return logs.strip()

    @staticmethod
    def _compare_output(actual, expected):
        """
        Compare outputs after normalizing whitespace and converting to lowercase.
        """
        norm_actual = ''.join(actual.split()).lower()
        norm_expected = ''.join(expected.split()).lower()
        return norm_actual == norm_expected


# Create a singleton CodeExecutor instance.
executor = CodeExecutor()


@app.before_first_request
def pull_docker_images():
    """
    Pre-pull all required Docker images for faster execution.
    """
    app.logger.info("Pre-pulling Docker images...")
    for lang, conf in executor.SUPPORTED_LANGUAGES.items():
        image = conf['image']
        try:
            executor.client.images.get(image)
            app.logger.info(f"Image {image} already exists.")
        except docker.errors.ImageNotFound:
            app.logger.info(f"Image {image} not found. Pulling...")
            try:
                executor.client.images.pull(image)
            except Exception as pull_ex:
                app.logger.error(f"Failed to pull image {image}: {pull_ex}")
        except Exception as e:
            app.logger.error(f"Error handling image {image}: {e}")


@app.route('/execute', methods=['POST'])
def execute():
    """
    /execute endpoint receives a JSON payload containing:
      - 'code': the user’s solution code,
      - 'language': the programming language, and
      - 'test_cases' (or a 'problem_id' to fetch them).
    
    It returns the aggregated test results.
    """
    app.logger.debug("Received /execute request")
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid JSON payload'}), 400

    code = data.get('code')
    language = data.get('language')
    problem_id = data.get('problem_id')
    test_cases = data.get('test_cases')

    # Use environment variable BACKEND_URL (defaulting to "http://backend:5000") when fetching test cases.
    if not test_cases and problem_id:
        try:
            backend_url = os.getenv("BACKEND_URL", "http://backend:5000")
            response = requests.get(f'{backend_url}/api/problems/{problem_id}/test-cases')
            if response.status_code == 200:
                test_cases = response.json()
            else:
                msg = f"Failed to fetch test cases for problem {problem_id}"
                app.logger.error(msg)
                return jsonify({'status': 'error', 'message': msg}), 400
        except Exception as e:
            msg = f"Error connecting to backend: {str(e)}"
            app.logger.error(msg)
            return jsonify({'status': 'error', 'message': msg}), 500

    if not code or not language or not test_cases:
        msg = "Missing required parameters: 'code', 'language', or 'test_cases'."
        app.logger.error(msg)
        return jsonify({'status': 'error', 'message': msg}), 400

    result = executor.execute_code(code, language, test_cases)
    return jsonify(result)


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    app.logger.debug("Starting Flask app on port 5001")
    app.run(host='0.0.0.0', port=5001)
