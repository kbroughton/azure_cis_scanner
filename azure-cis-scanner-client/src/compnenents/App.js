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
        <Route exact path='/security-center' component={SecurityCenter} />
        <Route exact path='/sql-servers' component={SQLServers} />
        <Route exact path='/logging-and-monitoring' component={LoggingAndMonitoring} />
        <Route exact path='/networking' component={Networking} />
        <Route exact path='/other-security-considerations' component={OtherSecurityConsiderations} />
        <Route exact path='/storage-accounts' component={StorageAccounts} />
        <Route exact path='/virtual-machines' component={VirtualMachines} />
        <Route exact path='/change-directory' component={Dashboard} />


      </div>  
    );
  }
}

export default App;
