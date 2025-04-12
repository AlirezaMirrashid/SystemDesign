import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const ProblemList = () => {
  const [problems, setProblems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    const fetchProblems = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/problems/');
        setProblems(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching problems:', err);
        setLoading(false);
      }
    };

    fetchProblems();
  }, []);

  const filteredProblems = filter === 'all' 
    ? problems 
    : problems.filter(problem => problem.difficulty === filter);

  const getDifficultyClass = (difficulty) => {
    switch(difficulty) {
      case 'easy': return 'difficulty-easy';
      case 'medium': return 'difficulty-medium';
      case 'hard': return 'difficulty-hard';
      default: return '';
    }
  };

  return (
    <div>
      <h2>Problems</h2>
      <div className="mb-4">
        <div className="btn-group" role="group">
          <button 
            className={`btn ${filter === 'all' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => setFilter('all')}
          >
            All
          </button>
          <button 
            className={`btn ${filter === 'easy' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => setFilter('easy')}
          >
            Easy
          </button>
          <button 
            className={`btn ${filter === 'medium' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => setFilter('medium')}
          >
            Medium
          </button>
          <button 
            className={`btn ${filter === 'hard' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => setFilter('hard')}
          >
            Hard
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : (
        <div className="row">
          {filteredProblems.map(problem => (
            <div className="col-md-6 mb-4" key={problem.id}>
              <div className="card problem-card h-100">
                <div className="card-body">
                  <h5 className="card-title">{problem.title}</h5>
                  <p className={`card-text ${getDifficultyClass(problem.difficulty)}`}>
                    {problem.difficulty.charAt(0).toUpperCase() + problem.difficulty.slice(1)}
                  </p>
                  <Link to={`/problems/${problem.id}`} className="btn btn-primary">
                    Solve
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProblemList;
