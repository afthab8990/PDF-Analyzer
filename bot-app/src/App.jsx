import { useState } from 'react';
import axios from 'axios';

function App() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    try {
      setLoading(true);
      const res = await axios.post('http://localhost:8000/ask', {
        query: query,
      });
      setResponse(res.data.answer);
    } catch (err) {
      setResponse('Error: ' + err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async () => {
    if (!file) return alert('Please select a PDF file.');
    const formData = new FormData();
    formData.append('file', file);
    try {
      setLoading(true);
      await axios.post('http://localhost:8000/upload-pdf', formData);
      alert('PDF uploaded and indexed successfully!');
    } catch (err) {
      alert('Upload error: ' + err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h1>📚 PDF AI Agent</h1>

      <div>
        <input type="file" accept="application/pdf" onChange={e => setFile(e.target.files[0])} />
        <button onClick={handleUpload} disabled={loading}>
          Upload PDF
        </button>
      </div>

      <br />

      <input
        type="text"
        placeholder="Ask a question..."
        value={query}
        onChange={e => setQuery(e.target.value)}
        style={{ width: '60%' }}
      />
      <button onClick={handleAsk} disabled={loading}>
        Ask
      </button>

      <div style={{ marginTop: '2rem' }}>
        <strong>Answer:</strong>
        <p>{loading ? 'Loading...' : response}</p>
      </div>
    </div>
  );
}

export default App;
