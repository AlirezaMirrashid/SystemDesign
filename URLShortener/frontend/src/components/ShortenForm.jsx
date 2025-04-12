import React, { useState } from "react";
import axios from "axios";

const ShortenForm = () => {
  const [originalUrl, setOriginalUrl] = useState("");
  const [customAlias, setCustomAlias] = useState("");
  const [expirationTime, setExpirationTime] = useState("");
  const [shortUrl, setShortUrl] = useState("");
  const [error, setError] = useState("");

  const backendUrl = process.env.REACT_APP_BACKEND_URL || "http://localhost:5001";

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setShortUrl("");

    try {
      const payload = {
        original_url: originalUrl,
        custom_alias: customAlias || undefined,
        expiration_time: expirationTime || undefined,
      };
      const response = await axios.post(`${backendUrl}/shorten`, payload);
      // setShortUrl(`${window.location.origin}/${response.data.short_url}`);
      setShortUrl(`${response.data.short_url}`);

    } catch (err) {
      setError(err.response?.data?.error || "An error occurred.");
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "1rem" }}>
          <label>Original URL:</label>
          <br />
          <input
            type="text"
            value={originalUrl}
            onChange={(e) => setOriginalUrl(e.target.value)}
            placeholder="https://example.com"
            style={{ width: "100%", padding: "0.5rem" }}
            required
          />
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label>Custom Alias (optional):</label>
          <br />
          <input
            type="text"
            value={customAlias}
            onChange={(e) => setCustomAlias(e.target.value)}
            placeholder="my-custom-alias"
            style={{ width: "100%", padding: "0.5rem" }}
          />
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label>Expiration Time (ISO8601 format, optional):</label>
          <br />
          <input
            type="text"
            value={expirationTime}
            onChange={(e) => setExpirationTime(e.target.value)}
            placeholder="2025-12-31T23:59:59"
            style={{ width: "100%", padding: "0.5rem" }}
          />
        </div>
        <button type="submit" style={{ padding: "0.5rem 1rem" }}>
          Shorten URL
        </button>
      </form>
      {shortUrl && (
        <div style={{ marginTop: "1rem" }}>
          <strong>Short URL:</strong> <a href={shortUrl}>{shortUrl}</a>
        </div>
      )}
      {error && (
        <div style={{ marginTop: "1rem", color: "red" }}>
          <strong>Error:</strong> {error}
        </div>
      )}
    </div>
  );
};

export default ShortenForm;
