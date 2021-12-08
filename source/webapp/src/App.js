import './App.css';
import React, {Component} from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import EmailsPage from './components/EmailsPage';

class App extends Component {

  render() {
    return (
      <BrowserRouter>
        <Routes>
          <Route path="/list-emails" element={<EmailsPage />} />
          <Route path="/" element={<Dashboard />} />
        </Routes>
    </BrowserRouter>
    )
  }
}

export default App;
