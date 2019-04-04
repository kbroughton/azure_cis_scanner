import React, { Component } from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { Link } from 'react-router-dom';
import { setService } from '../actions/subscriptions.js'

class Nav extends Component {
    
  handleClick = (service) => {
    console.log('selecting service')
    this.props.setService(service);
  }


  render() {
    
    const { selectedSubscription } = this.props;

    return (
      <nav>
          <li><Link to='/subscriptions'>Change Directory</Link></li>
          <li>  
            <Link to={`/${selectedSubscription}/security-center/Security%20Center`} 
              onClick={() => this.handleClick('Security%20Center')}>Security Center
            </Link>
          </li>
          <li>
            <Link to={`/${selectedSubscription}/storage-accounts/Storage%20Accounts`} 
              onClick={() => this.handleClick('Storage%20Accounts')}>Storage Accounts
            </Link>
          </li>
          <li>  
            <Link to={`/${selectedSubscription}/sql-servers/SQL%20Servers`} 
              onClick={() => this.handleClick('SQL%20Servers')}>SQL Servers
            </Link>
          </li>
          <li>  
            <Link to={`/${selectedSubscription}/logging-and-monitoring/Logging%20and%20Monitoring`} 
              onClick={() => this.handleClick('Logging%20and%20Monitoring')}>Logging and Monitoring
            </Link>
          </li>
          <li>  
            <Link to={`/${selectedSubscription}/networking/Networking`} 
              onClick={() => this.handleClick('Networking')}>Networking
            </Link>
          </li>
          <li>  
            <Link to={`/${selectedSubscription}/virtual-machines/Virtual%20Machines`} 
              onClick={() => this.handleClick('Virtual%20Machines')}>Virtual Machines
            </Link>
          </li>
          <li>  
            <Link to={`/${selectedSubscription}/other-security-considerations`} 
              onClick={() => this.handleClick('Other%20Security%20Considerations')}>Other Security Considerations
            </Link>
          </li>
      </nav>
    );
  }
}

const mapStateToProps = state => {
  return {
    subscriptions: state.subscriptions.subscriptions,
    selectedSubscription: state.subscriptions.selectedSubscription,
    service: state.subscriptions.service,
    finding: state.subscriptions.finding
  };
};

export default connect(
  mapStateToProps,
  dispatch => bindActionCreators({ setService }, dispatch),
  )(Nav);