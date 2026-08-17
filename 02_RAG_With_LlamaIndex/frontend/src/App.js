import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Task and Team Management</h1>
        <p>Frontend Mock UI</p>
      </header>
      <main>
        <h2>Task List</h2>
        <div className="task-list">
          <div className="task-item">
            <h3>Task 1: Initial project setup</h3>
            <p>Status: Completed</p>
          </div>
          <div className="task-item">
            <h3>Task 2: Design API endpoints</h3>
            <p>Status: In Progress</p>
          </div>
          <div className="task-item">
            <h3>Task 3: Build Frontend UI</h3>
            <p>Status: Pending</p>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
