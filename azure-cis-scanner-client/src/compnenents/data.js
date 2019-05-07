import React from "react";
import { Redirect } from "react-router-dom";
import { connect } from "react-redux";
import { bindActionCreators } from "redux";
import {
  selectService,
  setService,
  showStatToggle
} from "../actions/subscriptions";

class DisplayData extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      stat: "",
      statHeader: "",
      redirect: false
    };
    this.hideStat = this.hideStat.bind(this);
  }

  showStatHeader(e) {
    const stat = e
      .toLowerCase()
      .split(" ")
      .join("_");
    this.setState({
      statHeader: e,
      stat
    });
    this.props.showStatToggle(true);
  }

  hideStat() {
    this.props.showStatToggle(false);
  }

  componentDidMount() {
    const { service, selectedSubscription } = this.props;
    if (!service || !selectedSubscription) {
      console.log("return to dashboard");
      this.setState({
        redirect: true
      });
    } else if (service) {
      console.log("fetching data for", service);
      this.props.selectService(service);
    }
  }

  componentDidUpdate(prevProps) {
    const currentService = prevProps.service;
    const selectedService = this.props.match.params.services;
    if (currentService !== selectedService) {
      console.log("fetching data for ", selectedService);
      this.props.selectService(selectedService);
    }
  }

  render() {
    let data, statHeader;
    const {
      finding,
      selectedSubscription,
      stats,
      service,
      showStat
    } = this.props;
    const { stat } = this.state;
    // display header for which stat has been selected
    if (showStat) {
      statHeader = this.state.statHeader;
    } else {
      statHeader = "";
    }
    // if no subscription has been selected redirect to dashboard
    if (this.state.redirect) {
      console.log("no subscription selected");
      return <Redirect to="/subscriptions" />;
    }
    // render stat
    if (stat && showStat && stats[service].hasOwnProperty(stat)) {
      console.log(
        "rendering stats",
        // stat,
        showStat
        // stats[service].hasOwnProperty(stat)
      );
      const statData = stats[service][stat];
      data = Object.entries(statData).map((entry, index) => {
        let key = entry[0];
        let value = entry[1];
        return (
          <li className="stat" key={index.toString()}>
            {key}: {value}
          </li>
        );
      });
      // render findings
    } else if (finding) {
      data = finding.map((finding, index) => {
        let boundClick = this.showStatHeader.bind(this, finding[1]);
        return (
          <li className="data" key={index.toString()}>
            <button className="standard" onClick={boundClick}>
              {finding[0]}:{" "}
            </button>
            {finding[1]}
          </li>
        );
      });
      // render empty list if no findings exist
    } else {
      data = "";
    }

    return (
      <React.Fragment>
        <h4>Current Directory is {selectedSubscription}</h4>
        <a onClick={this.hideStat}>
          <h4>{service}</h4>
        </a>
        <h4>{statHeader}</h4>
        <ul>{data}</ul>
      </React.Fragment>
    );
  }
}

const mapStateToProps = state => {
  return {
    subscriptions: state.subscriptions.subscriptions,
    service: state.subscriptions.service,
    finding: state.subscriptions.finding,
    selectedSubscription: state.subscriptions.selectedSubscription,
    stats: state.subscriptions.stats,
    showStat: state.subscriptions.showStat
  };
};

export default connect(
  mapStateToProps,
  dispatch =>
    bindActionCreators({ selectService, setService, showStatToggle }, dispatch)
)(DisplayData);
