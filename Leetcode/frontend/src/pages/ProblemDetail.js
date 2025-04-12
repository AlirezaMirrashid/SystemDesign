
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import MonacoEditor from 'react-monaco-editor';

const defaultLanguageTemplates = {
  python: '# Write your Python solution here\n\nclass Solution:\n    def solve(self, *args):\n        # Your code here\n        pass',
  javascript: '// Write your JavaScript solution here\n\nclass Solution {\n    solve(...args) {\n        // Your code here\n    }\n}',
  java: '// Write your Java solution here\n\nclass Solution {\n    public int[] solve(int... args) {\n        // Your code here\n        return new int[0];\n    }\n}',
  cpp: '// Write your C++ solution here\n\n#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<int> solve(vector<int>& args) {\n        // Your code here\n        return {};\n    }\n};'
};

const ProblemDetail = () => {
  const { id } = useParams();
  const [problem, setProblem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [pollingId, setPollingId] = useState(null);
  const [pollingInterval, setPollingInterval] = useState(null);

  const languageOptions = [
    { value: 'python', label: 'Python' },
    { value: 'javascript', label: 'JavaScript' },
    { value: 'java', label: 'Java' },
    { value: 'cpp', label: 'C++' }
  ];

  // Fetch problem info from backend.
  useEffect(() => {
    const fetchProblem = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/api/problems/${id}`);
        setProblem(response.data);
        // Use the problem-specific starter code if available, otherwise fallback.
        if (response.data.starter_code && response.data.starter_code[language]) {
          setCode(response.data.starter_code[language]);
        } else {
          setCode(defaultLanguageTemplates[language]);
        }
        setLoading(false);
      } catch (err) {
        console.error('Error fetching problem:', err);
        setLoading(false);
      }
    };

    fetchProblem();
  }, [id, language]);

  // Polling effect for submission status.
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);

  // Start polling when we have a submission ID.
  useEffect(() => {
    if (pollingId) {
      const interval = setInterval(checkSubmissionStatus, 2000); // Poll every 2 sec.
      setPollingInterval(interval);
      return () => clearInterval(interval);
    }
  }, [pollingId]);

  const checkSubmissionStatus = async () => {
    if (!pollingId) return;
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:5000/api/submissions/status/${pollingId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const submissionData = response.data;
      if (submissionData.status !== 'pending' && submissionData.status !== 'processing') {
        setResult(submissionData);
        setSubmitting(false);
        setPollingId(null);
        if (pollingInterval) {
          clearInterval(pollingInterval);
          setPollingInterval(null);
        }
      } else if (submissionData.status === 'processing') {
        setResult({ status: 'processing', message: 'Your solution is being processed...' });
      }
    } catch (err) {
      console.error('Error checking submission status:', err);
      setSubmitting(false);
      setPollingId(null);
      if (pollingInterval) {
        clearInterval(pollingInterval);
        setPollingInterval(null);
      }
      setResult({ status: 'error', message: 'Failed to check submission status. Please try again.' });
    }
  };

  const handleLanguageChange = (e) => {
    const newLanguage = e.target.value;
    setLanguage(newLanguage);
    // When a new language is selected, check if problem has a starter code for that language.
    if (problem && problem.starter_code && problem.starter_code[newLanguage]) {
      setCode(problem.starter_code[newLanguage]);
    } else {
      setCode(defaultLanguageTemplates[newLanguage]);
    }
  };

  const handleCodeChange = (newCode) => setCode(newCode);

  const handleSubmit = async () => {
    if (!code.trim()) return;
    setSubmitting(true);
    setResult({ status: 'pending', message: 'Your solution has been queued for execution' });
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        'http://localhost:5000/api/submissions/',
        { problem_id: id, code, language },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setPollingId(response.data.submission_id);
    } catch (err) {
      console.error('Error submitting solution:', err);
      setResult({ status: 'error', message: 'Failed to submit solution. Please try again.' });
      setSubmitting(false);
    }
  };

  const editorOptions = {
    selectOnLineNumbers: true,
    roundedSelection: false,
    readOnly: false,
    cursorStyle: 'line',
    automaticLayout: true,
  };

  if (loading) {
    return (
      <div className="text-center">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (!problem) {
    return <div className="alert alert-danger">Problem not found</div>;
  }

  return (
    <div>
      <div className="mb-4">
        <h2>{problem.title}</h2>
        <span className={`badge ${problem.difficulty === 'easy' ? 'bg-success' : problem.difficulty === 'medium' ? 'bg-warning' : 'bg-danger'}`}>
          {problem.difficulty.charAt(0).toUpperCase() + problem.difficulty.slice(1)}
        </span>
      </div>

      <div className="row">
        <div className="col-md-5">
          <div className="card mb-4">
            <div className="card-header">Problem Description</div>
            <div className="card-body">
              <p className="card-text">{problem.description}</p>
              <h5>Examples:</h5>
              {problem.test_cases.map((testCase, index) => (
                <div key={index} className="mb-3">
                  <p><strong>Input:</strong> {testCase.input}</p>
                  <p><strong>Output:</strong> {testCase.expected}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="col-md-7">
          <div className="card mb-4">
            <div className="card-header d-flex justify-content-between align-items-center">
              <select className="form-select" value={language} onChange={handleLanguageChange}>
                {languageOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <button className="btn btn-primary" onClick={handleSubmit} disabled={submitting}>
                {submitting ? 'Submitting...' : 'Submit'}
              </button>
            </div>
            <div className="card-body p-0">
              <div className="editor-container">
                <MonacoEditor
                  width="100%"
                  height="100%"
                  language={language}
                  theme="vs-dark"
                  value={code}
                  options={editorOptions}
                  onChange={handleCodeChange}
                />
              </div>
            </div>
          </div>

          {result && (
            <div className={`card mb-4 ${result.status === 'accepted' ? 'border-success' : result.status === 'pending' || result.status === 'processing' ? 'border-warning' : 'border-danger'}`}>
              <div className={`card-header ${result.status === 'accepted' ? 'bg-success text-white' : result.status === 'pending' || result.status === 'processing' ? 'bg-warning text-dark' : 'bg-danger text-white'}`}>
                {result.status === 'accepted' ? 'Accepted' : result.status === 'pending' ? 'Pending' : result.status === 'processing' ? 'Processing' : 'Failed'}
              </div>
              <div className="card-body">
                {result.status === 'accepted' ? (
                  <div>
                    <p>All test cases passed!</p>
                    <p>Execution Time: {result.execution_time?.toFixed(2)}s</p>
                    <p>Memory Usage: {result.memory_usage}</p>
                  </div>
                ) : result.status === 'pending' || result.status === 'processing' ? (
                  <div>
                    <p>{result.message}</p>
                    <div className="progress">
                      <div className="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style={{ width: '100%' }}></div>
                    </div>
                  </div>
                ) : (
                  <div className="result-container">
                    <p>{result.message || 'Some test cases failed:'}</p>
                    {result.test_results && result.test_results.map((test, index) => (
                      <div key={index} className={`mb-3 ${test.passed ? 'test-case-passed' : 'test-case-failed'}`}>
                        <p><strong>Test Case {index + 1}:</strong> {test.passed ? 'Passed' : 'Failed'}</p>
                        {!test.passed && (
                          <>
                            <p><strong>Input:</strong> {test.test_case}</p>
                            <p><strong>Expected:</strong> {test.expected}</p>
                            <p><strong>Actual:</strong> {test.actual}</p>
                          </>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProblemDetail;
