import React from 'react';
import {connect} from 'react-redux';
import { bindActionCreators } from 'redux';
import { selectService } from '../actions/subscriptions';

class Networking extends React.Component {
    

    componentDidMount() {
        const service = this.props.match.params.services;
        this.props.selectService(service);
    }

    render() {
        
        return (
            <div>
                <p>The current directory is {this.props.selectedSubscription}</p>
            </div>
        );
    }
}

const mapStateToProps = state => {
    
    return {
      data: state.subscriptions.selectedServiceData,
      subscriptions: state.subscriptions.subscriptions,
      selectedSubscription: state.subscriptions.selectedSubscription
    };
};

export default connect(
    mapStateToProps,
    dispatch => bindActionCreators({ selectService }, dispatch),
    )(Networking);