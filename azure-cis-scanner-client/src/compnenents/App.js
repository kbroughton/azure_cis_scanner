import React, { Component } from 'react';
import {Route} from 'react-router-dom';
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
        <Route exact path='/subscriptions' component={Dashboard} />
        <Route exact path='/:subscriptionId/security-center/:services' component={SecurityCenter} />
        <Route exact path='/:subscriptionId/sql-servers/:services' component={SQLServers} />
        <Route exact path='/:subscriptionId/logging-and-monitoring/:services' component={LoggingAndMonitoring} />
        <Route exact path='/:subscriptionId/networking/:services' component={Networking} />
        <Route exact path='/:subscriptionId/other-security-considerations/:services' component={OtherSecurityConsiderations} />
        <Route exact path='/:subscriptionId/storage-accounts/:services' component={StorageAccounts} />
        <Route exact path='/:subscriptionId/virtual-machines/:services' component={VirtualMachines} />


      </div>  
    );
  }
}

export default App;
