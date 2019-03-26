import React, { Component } from 'react';
import { connect } from 'react-redux';
import {Link} from 'react-router-dom';

class Nav extends Component {
  
  render() {

    const selectedSubscription = this.props.selectedSubscription;

    return (
      <nav>
          <li><Link to='/subscriptions'>Change Directory</Link></li>
          <li><Link to={`/${selectedSubscription}/security-center/Security%20Center`}>Security Center</Link></li>
          <li><Link to={`/${selectedSubscription}/storage-accounts/Storage%20Accounts`}>Storage Accounts</Link></li>
          <li><Link to={`/${selectedSubscription}/sql-servers/SQL%20Servers`}>SQL Servers</Link></li>
          <li><Link to={`/${selectedSubscription}/logging-and-monitoring/Logging%20and%20Monitoring`}>Logging and Monitoring</Link></li>
          <li><Link to={`/${selectedSubscription}/networking/Networking`}>Networking</Link></li>
          <li><Link to={`/${selectedSubscription}/virtual-machines/Virtual%20Machines`}>Virtual Machines</Link></li>
          <li><Link to={`/${selectedSubscription}/other-security-considerations`}>Other Security Considerations</Link></li>
      </nav>
    );
  }
}

export default connect(
  state => ({ selectedSubscription: state.subscriptions.selectedSubscription })
)(Nav);