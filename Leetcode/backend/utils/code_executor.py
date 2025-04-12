import requests

def execute_code(code, language, problem_id):
    """
    Send code execution request to the code-executor service
    
    Args:
        code (str): The code to execute
        language (str): The programming language
        problem_id (str): The ID of the problem
        
    Returns:
        dict: The execution result
    """
    try:
        # Make a request to the code-executor service
        response = requests.post(
            'http://code-executor:5001/execute',
            json={
                'code': code,
                'language': language,
                'problem_id': problem_id
            },
            timeout=30  # Set a reasonable timeout
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
        else:
            # Handle error response
            return {
                'status': 'error',
                'message': f'Code execution service returned error: {response.text}'
            }
    except requests.RequestException as e:
        # Handle connection errors
        return {
            'status': 'error',
            'message': f'Failed to connect to code execution service: {str(e)}'
        }
