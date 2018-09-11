import React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import {getSubscriptions, selectSubscription} from '../actions/dashboard';

class Dashboard extends React.Component {
    componentDidMount() {
        if (!this.props.selectedSubscription) {
            this.props.getSubscriptions();
        }
    }

    render() {
        const {subscriptions} = this.props;
        let options;
        let selected;
       
        if (this.props.subscriptions) {
            options = subscriptions.map((subscription, index) => {
                let selected;
                console.log(this.props.selectedSubscription, subscription)
                if (this.props.selectedSubscription === subscription.id) {
                    selected = "selected"
                }
                return <option key={index} selected={selected} value={subscription.id}>{subscription.name}</option>
            })
            }
        
        return (
            <form>
                <label htmlFor='selected-sub-directory'>Select a Directory</label>
                <select className='selected-sub-directory' 
                    name='selected-sub-directory' 
                    onChange={e => this.props.selectSubscription(e.target.value)}
                    >
                      <option value="">Please select an option</option>
                      {options}
                </select> 
            </form>
        );
    }
}

const mapStateToProps = state => {
    console.log(state)
    return {
      subscriptions: state.subscriptions.subscriptions,
      selectedSubscription: state.subscriptions.selectedSubscription
    };
};

export default connect(
    mapStateToProps,
    dispatch => bindActionCreators({ selectSubscription, getSubscriptions }, dispatch),
)(Dashboard);
