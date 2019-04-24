import React, { Component } from "react";
import { connect } from "react-redux";
import { bindActionCreators } from "redux";
import { Link } from "react-router-dom";
import { setService, getCis } from "../actions/subscriptions.js";

class Nav extends Component {
  handleClick = service => {
    console.log("selecting service");
    this.props.setService(service);
  };

  componentDidMount() {
    this.props.getCis();
  }

  render() {
    const { nav } = this.props;
    let navLinks;
    if (nav) {
      navLinks = nav.map((n, key) => {
        return (
          <li key={key}>
            {" "}
            <Link
              to={`/services/${n}`}
              onClick={() => this.handleClick(`${n}`)}
            >
              {n}
            </Link>
          </li>
        );
      });
    }

    return (
      <nav>
        <li>
          <Link to="/subscriptions">Change Directory</Link>
        </li>
        {navLinks}
      </nav>
    );
  }
}

const mapStateToProps = state => {
  return {
    nav: state.subscriptions.nav,
    subscriptions: state.subscriptions.subscriptions,
    selectedSubscription: state.subscriptions.selectedSubscription,
    service: state.subscriptions.service,
    finding: state.subscriptions.finding
  };
};

export default connect(
  mapStateToProps,
  dispatch => bindActionCreators({ setService, getCis }, dispatch)
)(Nav);
