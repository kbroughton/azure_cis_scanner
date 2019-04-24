import React from "react";
import { Redirect } from "react-router-dom";
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
      redirect: false
    };
  }

  seeStat(e) {
    const stat = e
      .toLowerCase()
      .split(" ")
      .join("_");
    this.setState({
      stat
    });
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
    let data, header;
    const { finding, selectedSubscription, stats, service } = this.props;
    const { stat } = this.state;
    // if no subscription has been selected redirect to dashboard
    if (this.state.redirect) {
      console.log("no subscription selected");
      return <Redirect to="/subscriptions" />;
    }
    // render stat
    if (stat && stats[service].hasOwnProperty(stat)) {
      const statData = stats[service][stat];
      header = stat;
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
      header = service;
      data = finding.map((finding, index) => {
        let boundClick = this.seeStat.bind(this, finding[1]);
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
        <h3>Current Directory is {selectedSubscription}</h3>
        <h3>{header}</h3>
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
