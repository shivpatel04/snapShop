import React, { useState } from "react";
import axios from "axios";
import Loader from "./Loader";
import ResultsTable from "./ResultsTable";
import { Button, Typography, Box } from "@mui/material";

const UploadForm = () => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    const uploadedFile = e.target.files[0];
    setFile(uploadedFile);
    if (uploadedFile) {
      const reader = new FileReader();
      reader.onload = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(uploadedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("image", file);

    try {
      const response = await axios.post("http://localhost:8000/search", formData);
      setResults(response.data.results);
    } catch (error) {
      console.error(error);
      alert("Upload failed!");
    }
    setLoading(false);
  };

  return (
    <Box textAlign="center" mt={4}>
      <Typography variant="h4" gutterBottom>
        Snap-to-Shop Visual Search
      </Typography>

      <input type="file" onChange={handleFileChange} />
      <br /><br />
      <Button variant="contained" color="primary" onClick={handleUpload}>
        Upload & Search
      </Button>

      {preview && (
        <Box mt={3}>
          <Typography variant="h6">Preview:</Typography>
          <img src={preview} alt="Uploaded preview" style={{ maxWidth: "200px", borderRadius: "8px",boxShadow: "0 0 10px rgba(0,0,0,0.5)", marginTop: "10px" }} />
        </Box>
      )}

      {loading && <Loader />}
      {results.length > 0 && <ResultsTable data={results} />}
    </Box>
  );
};

export default UploadForm;
