import React, { Component } from 'react';
import {Link} from 'react-router-dom';
import './App.css';

class Nav extends Component {
  
  render() {

    
    return (
      <nav>
          <li>Azure Foundations Benchmark 1.0</li>
          <li><Link to='/'>Change Directory</Link></li>
          <li><Link to='/security-center'>Security Center</Link></li>
          <li><Link to='/storage-accounts'>Storage Accounts</Link></li>
          <li><Link to='sql-servers'>SQL Servers</Link></li>
          <li><Link to='logging-and-monitoring'>Logging and Monitoring</Link></li>
          <li><Link to='networking'>Networking</Link></li>
          <li><Link to='virtual-machines'>Virtual Machines</Link></li>
          <li><Link to='other-security-considerations'>Other Security Considerations</Link></li>
      </nav>
    );
  }
}

export default Nav;