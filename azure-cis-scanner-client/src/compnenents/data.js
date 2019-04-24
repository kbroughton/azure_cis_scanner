import React from "react";
import { Redirect, Link } from "react-router-dom";
import { connect } from "react-redux";
import { bindActionCreators } from "redux";
import { selectService, setService } from "../actions/subscriptions";

class DisplayData extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      dataList: true,
      findingList: false,
      stat: false,
      prettyStat: "",
      redirect: false
    };
    this.hideStat = this.hideStat.bind(this);
  }

  showStat(e) {
    const stat = e
      .toLowerCase()
      .split(" ")
      .join("_");
    this.setState({
      prettyStat: e,
      stat
    });
  }

  hideStat() {
    this.setState({ stat: false });
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
      this.props.selectService(this.props.match.params.services);
    }
  }

  render() {
    let data;
    const { finding, selectedSubscription, stats, service } = this.props;
    const { stat, prettyStat } = this.state;
    // if no subscription has been selected redirect to dashboard
    if (this.state.redirect) {
      console.log("no subscription selected");
      return <Redirect to="/subscriptions" />;
    }
    // render stat
    if (stat && stats[service].hasOwnProperty(stat)) {
      const statData = stats[service][stat];
      data = Object.entries(statData).map((entry, index) => {
        let key = entry[0];
        let value = entry[1];
        console.log(key, value);
        return (
          <li key={index.toString()}>
            {key}: {value}
          </li>
        );
      });
      // render findings
    } else if (finding) {
      data = finding.map((finding, index) => {
        let boundClick = this.showStat.bind(this, finding[1]);
        return (
          <li className="data" key={index.toString()}>
            <button className="standard" onClick={boundClick}>
              {finding[0]}:{" "}
            </button>
            {finding[1]}
          </li>
        );
      });
      // render empty list
    } else if (!finding) {
      data = "";
    }

    return (
      <React.Fragment>
        <h4>Current Directory is {selectedSubscription}</h4>
        <a onClick={this.hideStat}>
          <h4>{service}</h4>
        </a>
        <h4>{prettyStat}</h4>
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
    stats: state.subscriptions.stats
  };
};

export default connect(
  mapStateToProps,
  dispatch => bindActionCreators({ selectService, setService }, dispatch)
)(DisplayData);
