import React, { Component } from 'react';
import {Route} from 'react-router-dom';
import './App.css';
import Nav from './nav';
import Header from './header';
import Dashboard from './dashboard';
import SecurityCenter from './security-center';
import SQLServers from './sql-servers';
import LoggingAndMonitoring from './logging-and-monitoring';
import Networking from './networking';
import OtherSecurityConsiderations from './other-security-considerations';
import StorageAccounts from './storage-accounts';
import VirtualMachines from './virtual-machines';

class App extends Component {
  
  
  render() {
    
    return (
      <div>
        <Nav />
        <Header />
        <Route exact path='/' component={Dashboard} />
        <Route exact path='/:subscriptionId/security-center' component={SecurityCenter} />
        <Route exact path='/:subscriptionId/sql-servers' component={SQLServers} />
        <Route exact path='/:subscriptionId/logging-and-monitoring' component={LoggingAndMonitoring} />
        <Route exact path='/:subscriptionId/networking' component={Networking} />
        <Route exact path='/:subscriptionId/other-security-considerations' component={OtherSecurityConsiderations} />
        <Route exact path='/:subscriptionId/storage-accounts' component={StorageAccounts} />
        <Route exact path='/:subscriptionId/virtual-machines' component={VirtualMachines} />
        <Route exact path='/:subscriptionId/change-directory' component={Dashboard} />


      </div>  
    );
  }
}

export default App;
