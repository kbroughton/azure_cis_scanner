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
      console.log("dispatching selectService for ", service);
      this.props.selectService(service);
    }
  }

  componentDidUpdate(prevProps) {
    const service = prevProps.service;
    console.log(service, ":that's the prevService");
    if (!service) {
      console.log("service is null");
    } else if (this.props.match.params.services !== service) {
      console.log(
        "swithcing from ",
        service,
        " to ",
        this.props.match.params.services
      );
      this.props.selectService(this.props.match.params.services);
    }
  }

  render() {
    let dataList;
    const { finding, selectedSubscription } = this.props;

    if (this.state.redirect) {
      return <Redirect to="/subscriptions" />;
    }
    if (finding) {
      console.log("render findings");
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
