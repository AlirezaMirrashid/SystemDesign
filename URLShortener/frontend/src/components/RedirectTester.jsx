// // // In frontend/src/components/RedirectTester.jsx
// // import React, { useState } from "react";

// // const RedirectTester = () => {
// //   const [shortCode, setShortCode] = useState("");

// //   const handleTest = () => {
// //     // This assumes your read service is reachable at this URL.
// //     window.location.href = `http://localhost:5002/${shortCode}`;
// //   };

// //   return (
// //     <div style={{ marginTop: "2rem" }}>
// //       <h3>Test Redirect</h3>
// //       <input
// //         type="text"
// //         placeholder="Enter short code"
// //         value={shortCode}
// //         onChange={(e) => setShortCode(e.target.value)}
// //       />
// //       <button onClick={handleTest}>Go</button>
// //     </div>
// //   );
// // };

// // export default RedirectTester;


// // frontend/src/components/RedirectTester.jsx
// import React, { useState } from "react";
// import axios from "axios";

// const RedirectTester = () => {
//   const [shortUrlInput, setShortUrlInput] = useState("");
//   const [originalUrl, setOriginalUrl] = useState("");
//   const [error, setError] = useState("");

//   const handleLookupAndRedirect = async () => {
//     let code = shortUrlInput.trim();
//     // If user enters a full URL, extract the code (assuming it's the last segment)
//     if (code.includes('/')) {
//       const parts = code.split('/');
//       code = parts[parts.length - 1];
//     }
//     try {
//       const response = await axios.get(`/lookup/${code}`);
//       const url = response.data.original_url;
//       setOriginalUrl(url);
//       setError("");
//       // Automatically redirect after 2 seconds
//       setTimeout(() => {
//         window.location.href = url;
//       }, 2000);
//     } catch (err) {
//       setError(err.response?.data?.error || "Error retrieving original URL");
//       setOriginalUrl("");
//     }
//   };

//   return (
//     <div>
//       <h2>Lookup &amp; Redirect</h2>
//       <input
//         type="text"
//         placeholder="Enter short URL or code"
//         value={shortUrlInput}
//         onChange={(e) => setShortUrlInput(e.target.value)}
//         style={{ marginRight: "0.5rem" }}
//       />
//       <button onClick={handleLookupAndRedirect}>Lookup &amp; Redirect</button>
//       {originalUrl && (
//         <div style={{ marginTop: "1rem" }}>
//           <strong>Original URL:</strong> {originalUrl}
//         </div>
//       )}
//       {error && (
//         <div style={{ marginTop: "1rem", color: "red" }}>{error}</div>
//       )}
//     </div>
//   );
// };

// export default RedirectTester;


// frontend/src/components/RedirectTester.jsx
import React, { useState } from "react";
import axios from "axios";

const RedirectTester = () => {
  const [shortUrlInput, setShortUrlInput] = useState("");
  const [originalUrl, setOriginalUrl] = useState("");
  const [error, setError] = useState("");

  const handleLookupAndRedirect = async () => {
    let code = shortUrlInput.trim();
    console.log("Raw input:", shortUrlInput);
    // If user enters a full URL, extract the code (assuming it's the last segment)
    if (code.includes('/')) {
      const parts = code.split('/');
      code = parts[parts.length - 1];
      console.log("Extracted short code from full URL:", code);
    } else {
      console.log("Short code:", code);
    }

    try {
      // const response = await axios.get(`/lookup/${code}`);
      const response = await axios.get(`http://localhost:5002/lookup/${code}`);
      console.log("Lookup response:", response.data);
      const url = response.data.original_url;
      setOriginalUrl(url);
      setError("");
      // Automatically redirect after 2 seconds
      // setTimeout(() => {
      //   console.log("Redirecting to:", url);
      //   window.location.href = url;
      // }, 2000);
      // Automatically open the URL in a new tab after 2 seconds
      setTimeout(() => {
        console.log("Opening URL in new tab:", url);
        window.open(url, '_blank');
      }, 2000);
    } catch (err) {
      console.error("Error during lookup:", err);
      setError(err.response?.data?.error || "Error retrieving original URL");
      setOriginalUrl("");
    }
  };

  return (
    <div>
      <h2>Lookup &amp; Redirect</h2>
      <input
        type="text"
        placeholder="Enter short URL or code"
        value={shortUrlInput}
        onChange={(e) => setShortUrlInput(e.target.value)}
        style={{ marginRight: "0.5rem" }}
      />
      <button onClick={handleLookupAndRedirect}>Lookup &amp; Redirect</button>
      {originalUrl && (
        <div style={{ marginTop: "1rem" }}>
          <strong>Original URL:</strong> {originalUrl}
        </div>
      )}
      {error && (
        <div style={{ marginTop: "1rem", color: "red" }}>{error}</div>
      )}
    </div>
  );
};

export default RedirectTester;
