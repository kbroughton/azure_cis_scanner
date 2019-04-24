import React, { Component } from "react";
import { Route } from "react-router-dom";
import Nav from "./nav";
import Header from "./header";
import Dashboard from "./dashboard";
import DisplayData from "./data";

class App extends Component {
  render() {
    return (
      <div>
        <Nav />
        <Header />
        <Route exact path="/" component={Dashboard} />
        <Route exact path="/subscriptions" component={Dashboard} />
        <Route exact path="/services/:services" component={DisplayData} />
      </div>
    );
  }
}

export default App;
