// // frontend/src/components/OriginalUrlLookup.jsx
// import React, { useState } from 'react';
// import axios from 'axios';

// const OriginalUrlLookup = () => {
//   const [shortUrlInput, setShortUrlInput] = useState('');
//   const [originalUrl, setOriginalUrl] = useState('');
//   const [error, setError] = useState('');

//   const handleLookup = async () => {
//     // Extract the short code from the entered string.
//     // If the user enters a full URL (e.g., "http://short.ly/abcd123"),
//     // we'll extract the part after the last "/".
//     let code = shortUrlInput.trim();
//     if (code.includes('/')) {
//       const parts = code.split('/');
//       code = parts[parts.length - 1];
//     }

//     try {
//       const response = await axios.get(`/lookup/${code}`);
//       setOriginalUrl(response.data.original_url);
//       setError('');
//     } catch (err) {
//       setError(err.response?.data?.error || 'Error retrieving original URL');
//       setOriginalUrl('');
//     }
//   };

//   return (
//     <div>
//       <h2>Lookup Original URL</h2>
//       <input
//         type="text"
//         placeholder="Enter short URL or code"
//         value={shortUrlInput}
//         onChange={(e) => setShortUrlInput(e.target.value)}
//         style={{ marginRight: '0.5rem' }}
//       />
//       <button onClick={handleLookup}>Lookup</button>
//       {originalUrl && (
//         <div style={{ marginTop: '1rem' }}>
//           <strong>Original URL:</strong> {originalUrl}
//         </div>
//       )}
//       {error && (
//         <div style={{ marginTop: '1rem', color: 'red' }}>{error}</div>
//       )}
//     </div>
//   );
// };

// export default OriginalUrlLookup;


// frontend/src/components/DisplayOriginalUrl.jsx
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";

const DisplayOriginalUrl = () => {
  const { shortCode } = useParams();
  const [originalUrl, setOriginalUrl] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchOriginalUrl = async () => {
      try {
        const response = await axios.get(`/lookup/${shortCode}`);
        setOriginalUrl(response.data.original_url);
        setError("");
      } catch (err) {
        setError(err.response?.data?.error || "Error fetching original URL");
      }
      setLoading(false);
    };

    fetchOriginalUrl();
  }, [shortCode]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div style={{ color: "red" }}>{error}</div>;

  return (
    <div>
      <h2>Mapping for: {shortCode}</h2>
      <p>
        <strong>Original URL:</strong> {originalUrl}
      </p>
    </div>
  );
};

export default DisplayOriginalUrl;
