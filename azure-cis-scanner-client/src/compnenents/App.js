import React, { Component } from 'react';
import {Route} from 'react-router-dom';
import Nav from './nav';
import Header from './header';
import Dashboard from './dashboard';
import DisplayData from './data-template';

class App extends Component {
  
  
  render() {
    
    return (
      <div>
        <Nav />
        <Header />
        <Route exact path='/' component={Dashboard} />
        <Route exact path='/subscriptions' component={Dashboard} />
        <Route exact path='/:subscriptionId/security-center/:services' component={DisplayData}/>
        <Route exact path='/:subscriptionId/sql-servers/:services' component={DisplayData}/>
        <Route exact path='/:subscriptionId/logging-and-monitoring/:services' component={DisplayData}/>
        <Route exact path='/:subscriptionId/networking/:services' component={DisplayData}/>
        <Route exact path='/:subscriptionId/other-security-considerations/:services' component={DisplayData}/>
        <Route exact path='/:subscriptionId/storage-accounts/:services' component={DisplayData}/>
        <Route exact path='/:subscriptionId/virtual-machines/:services' component={DisplayData}/>


      </div>  
    );
  }
}

export default App;
