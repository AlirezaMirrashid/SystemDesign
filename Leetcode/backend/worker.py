import time
import json
import redis
from utils.code_executor import execute_code
from models.submission import Submission
from models.problem import Problem

def worker_main():
    """
    Main worker function that processes code execution jobs from the Redis queue
    """
    print("Starting code execution worker...")
    
    # Initialize Redis connection
    redis_client = redis.Redis(host='redis', port=6379, db=0)
    
    while True:
        try:
            # Get a job from the queue with blocking pop
            # This will wait for a new job if the queue is empty
            queue_data = redis_client.brpop('code_execution_queue', timeout=0)
            
            if queue_data:
                # queue_data is a tuple (queue_name, job_data)
                _, job_data_bytes = queue_data
                job_data = json.loads(job_data_bytes)
                
                print(f"Processing submission: {job_data['submission_id']}")
                
                # Extract job details
                submission_id = job_data['submission_id']
                problem_id = job_data['problem_id']
                code = job_data['code']
                language = job_data['language']
                
                # Update submission status to processing
                Submission.update_status(submission_id, 'processing')
                
                # Get problem test cases
                problem = Problem.find_by_id(problem_id)
                if not problem:
                    Submission.update_status(
                        submission_id, 
                        'error', 
                        test_results=[{'error': 'Problem not found'}]
                    )
                    continue
                
                # Execute the code
                result = execute_code(code, language, problem_id)
                
                # Update the submission with the results
                Submission.update_status(
                    submission_id,
                    result['status'],
                    execution_time=result.get('execution_time'),
                    memory_usage=result.get('memory_usage'),
                    test_results=result.get('test_results')
                )
                
                print(f"Completed submission: {submission_id} with status: {result['status']}")
                
        except Exception as e:
            print(f"Error processing job: {str(e)}")
            # Sleep briefly to avoid tight loop in case of persistent errors
            time.sleep(1)

if __name__ == "__main__":
    worker_main()
