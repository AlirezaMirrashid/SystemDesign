import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Profile = () => {
  const [profile, setProfile] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfileData = async () => {
      try {
        const token = localStorage.getItem('token');
        
        // Fetch user profile
        const profileResponse = await axios.get(
          'http://localhost:5000/api/auth/profile',
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );
        
        // Fetch user submissions
        const submissionsResponse = await axios.get(
          'http://localhost:5000/api/submissions/user',
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );
        
        setProfile(profileResponse.data);
        setSubmissions(submissionsResponse.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching profile data:', err);
        setLoading(false);
      }
    };

    fetchProfileData();
  }, []);

  if (loading) {
    return (
      <div className="text-center">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (!profile) {
    return <div className="alert alert-danger">Failed to load profile</div>;
  }

  return (
    <div>
      <div className="row">
        <div className="col-md-4">
          <div className="card mb-4">
            <div className="card-header">Profile</div>
            <div className="card-body">
              <h5 className="card-title">{profile.username}</h5>
              <p className="card-text">Email: {profile.email}</p>
              <p className="card-text">Problems Solved: {profile.solved_problems.length}</p>
            </div>
          </div>
        </div>
        
        <div className="col-md-8">
          <div className="card">
            <div className="card-header">Recent Submissions</div>
            <div className="card-body">
              {submissions.length === 0 ? (
                <p>No submissions yet.</p>
              ) : (
                <div className="table-responsive">
                  <table className="table table-striped">
                    <thead>
                      <tr>
                        <th>Problem</th>
                        <th>Language</th>
                        <th>Status</th>
                        <th>Time</th>
                        <th>Date</th>
                      </tr>
                    </thead>
                    <tbody>
                      {submissions.map(submission => (
                        <tr key={submission.id}>
                          <td>{submission.problem_id}</td>
                          <td>{submission.language}</td>
                          <td>
                            <span className={`badge ${submission.status === 'accepted' ? 'bg-success' : 'bg-danger'}`}>
                              {submission.status}
                            </span>
                          </td>
                          <td>{submission.execution_time ? `${submission.execution_time.toFixed(2)}s` : 'N/A'}</td>
                          <td>{new Date(submission.timestamp).toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
