import React, { Component } from 'react';
import { connect } from 'react-redux';
import {Link} from 'react-router-dom';
import './App.css';

class Nav extends Component {
  
  render() {

    const selectedSubscription = this.props.selectedSubscription;

    return (
      <nav>
          <li>Azure Foundations Benchmark 1.0</li>
          <li><Link to='/'>Change Directory</Link></li>
          <li><Link to={`/${selectedSubscription}/security-center`}>Security Center</Link></li>
          <li><Link to={`/${selectedSubscription}/storage-accounts`}>Storage Accounts</Link></li>
          <li><Link to={`/${selectedSubscription}/sql-servers`}>SQL Servers</Link></li>
          <li><Link to={`/${selectedSubscription}/logging-and-monitoring`}>Logging and Monitoring</Link></li>
          <li><Link to={`/${selectedSubscription}/networking`}>Networking</Link></li>
          <li><Link to={`/${selectedSubscription}/virtual-machines`}>Virtual Machines</Link></li>
          <li><Link to={`/${selectedSubscription}/other-security-considerations`}>Other Security Considerations</Link></li>
      </nav>
    );
  }
}

export default connect(
  state => ({ selectedSubscription: state.subscriptions.selectedSubscription })
)(Nav);