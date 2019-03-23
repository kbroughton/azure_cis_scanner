import React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import {getSubscriptions, selectSubscription} from '../actions/subscriptions';

class Dashboard extends React.Component {

    componentDidMount() {
        if (!this.props.selectedSubscription || this.props.selectedSubscription.length === 0) {
            this.props.getSubscriptions();
        }
    }

    render() {
        
        let options;
        if (this.props.subscriptions) {
            let {subscriptions} = this.props;
            subscriptions = subscriptions.replace(/'/g, '"');
            subscriptions = JSON.parse(subscriptions)
            options = subscriptions.map((subscription, index) => {
                return <option key={index} value={subscription}>{subscription}</option>
            })
        }
        
        return (
            <form>
                <label htmlFor='selected-sub-directory'>Select a Directory:</label>
                <select className='selected-sub-directory' 
                    name='selected-sub-directory' value={this.props.selectedSubscription}
                    onChange={e => this.props.selectSubscription(e.target.value)}
                    >
                      {options}
                </select> 
            </form>
        );
    }
}

const mapStateToProps = state => {
    return {
      subscriptions: state.subscriptions.subscriptions,
      selectedSubscription: state.subscriptions.selectedSubscription
    };
};

export default connect(
    mapStateToProps,
    dispatch => bindActionCreators({ selectSubscription, getSubscriptions }, dispatch),
)(Dashboard);
