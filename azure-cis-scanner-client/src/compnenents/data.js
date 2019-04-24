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
      redirect: false
    };
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
    if (!currentService) {
      return;
    } else if (currentService !== selectedService) {
      console.log("fetching data for ", selectedService);
      this.props.selectService(this.props.match.params.services);
    }
  }

  render() {
    let dataList;
    const { finding, selectedSubscription } = this.props;

    if (this.state.redirect) {
      console.log("no subscription selected");
      return <Redirect to="/subscriptions" />;
    }
    // render findings as a list if data exists
    if (finding) {
      dataList = finding.map((finding, index) => {
        return (
          <li className="data" key={index.toString()}>
            <span className="standard">{finding[0]}: </span>
            {finding[1]}
          </li>
        );
      });
    } else if (!finding) {
      dataList = "";
    }

    return (
      <React.Fragment>
        <h3>Current Directory is {selectedSubscription}</h3>
        <ul>{dataList}</ul>
      </React.Fragment>
    );
  }
}

const mapStateToProps = state => {
  return {
    subscriptions: state.subscriptions.subscriptions,
    service: state.subscriptions.service,
    finding: state.subscriptions.finding,
    selectedSubscription: state.subscriptions.selectedSubscription
  };
};

export default connect(
  mapStateToProps,
  dispatch => bindActionCreators({ selectService, setService }, dispatch)
)(DisplayData);
