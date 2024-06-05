import React from 'react';
import './App.css';
import ConversationsList from './components/startingPage';
import DialoguePage from './components/conversationPage'; // Adjust the path as necessary
import {
  BrowserRouter as Router,
  Routes,
  Route,
} from 'react-router-dom';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<ConversationsList />} />
        <Route path="/conversation/:id" element={<DialoguePage />} />
      </Routes>
    </Router>
  );
}

export default App;
