import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
  return (
    <div className="jumbotron text-center">
      <h1 className="display-4">Welcome to CodeChallenge</h1>
      <p className="lead">
        Improve your coding skills by solving programming problems in multiple languages.
      </p>
      <hr className="my-4" />
      <p>
        Start solving problems, track your progress, and prepare for technical interviews.
      </p>
      <Link to="/problems" className="btn btn-primary btn-lg">
        Start Coding
      </Link>
    </div>
  );
};

export default Home;
