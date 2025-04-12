// // in frontend/src/app.jsx
// import react from "react";
// import ShortenForm from "./components/ShortenForm";
// import RedirectTester from "./components/RedirectTester";

// const app = () => {
//   return (
//     <div style={{ margin: "2rem", fontfamily: "arial, sans-serif" }}>
//       <h1>url shortener</h1>
//       <ShortenForm />
//       <RedirectTester />
//     </div>
//   );
// };

// export default App;

// // import React from "react";
// // import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
// // import ShortenForm from "./components/ShortenForm";
// // import RedirectTester from "./components/RedirectTester";

// // const App = () => {
  // // return (
    // // <Router>
      // // <Routes>
        // // <Route path="/" element={<ShortenForm />} />
        // // {/* If it's not a known React route, redirect to the backend */}
        // // <Route path="*" element={<ExternalRedirect />} />
      // // </Routes>
    // // </Router>
  // // );
// // };

// // // This component redirects short URLs
// // const ExternalRedirect = () => {
  // // window.location.href = window.location.href; // This triggers the backend redirect
  // // return null; // Prevent React from rendering anything
// // };

// // export default App;

// import React from "react";
// import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
// import ShortenForm from "./components/ShortenForm";
// import RedirectTester from "./components/RedirectTester";

// // Component that triggers a full reload so that the backend handles the redirect
// const ExternalRedirect = () => {
  // window.location.href = window.location.href;
  // return null;
// };

// const App = () => {
  // return (
    // <Router>
      // <div style={{ margin: "2rem", fontFamily: "Arial, sans-serif" }}>
        // <h1>URL Shortener</h1>
        // <Routes>
          // <Route path="/" element={<ShortenForm />} />
          // <Route path="/test" element={<RedirectTester />} />
          // {/* Catch-all route: any unknown path triggers a full reload */}
          // <Route path="*" element={<ExternalRedirect />} />
        // </Routes>
      // </div>
    // </Router>
  // );
// };

// export default App;



// // frontend/src/App.jsx
// import React from "react";
// import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
// import ShortenForm from "./components/ShortenForm";
// import RedirectTester from "./components/RedirectTester";
// import DisplayOriginalUrl from "./components/DisplayOriginalUrl";

// const App = () => {
//   return (
//     <Router>
//       <div style={{ margin: "2rem", fontFamily: "Arial, sans-serif" }}>
//         <h1>URL Shortener</h1>
//         <Routes>
//           <Route path="/" element={<ShortenForm />} />
//           <Route path="/test" element={<RedirectTester />} />
//           {/* Route to handle a short code and display the original URL */}
//           <Route path="/:shortCode" element={<DisplayOriginalUrl />} />
//         </Routes>
//       </div>
//     </Router>
//   );
// };

// export default App;


// frontend/src/App.jsx
import React from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import ShortenForm from "./components/ShortenForm";
import RedirectTester from "./components/RedirectTester";
import DisplayOriginalUrl from "./components/DisplayOriginalUrl";

const App = () => {
  return (
    <Router>
      <div style={{ margin: "2rem", fontFamily: "Arial, sans-serif" }}>
        <h1>URL Shortener</h1>
        <nav style={{ marginBottom: "1rem" }}>
          <Link to="/">Shorten URL</Link> |{" "}
          <Link to="/redirect-tester">Lookup &amp; Redirect</Link>
        </nav>
        <Routes>
          <Route path="/" element={<ShortenForm />} />
          <Route path="/redirect-tester" element={<RedirectTester />} />
          {/* This route handles direct URL access, if needed */}
          <Route path="/:shortCode" element={<DisplayOriginalUrl />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
