import { useState, useEffect } from 'react';
import './App.css'

const App = () => {
  const [message, setMessage] = useState<string>('');

  useEffect(() => {
    fetch('http://localhost:8000/api/v1')
      .then(response => response.json())
      .then(data => setMessage(data.message));
  }, []);

  return <div className="container">{message ? <p>{message}</p> : <p>Loading...</p>}</div>;
};

export default App;
