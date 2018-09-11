import React from 'react';
import {connect} from 'react-redux';
import {getSubscriptions, selectSubscription} from '../actions/dashboard';

class Dashboard extends React.Component {
    constructor(props) {
        super(props);
       
        this.select;
        this.selectRef = select => {
            this.select = select
        }
    }

    componentDidMount() {
        if (!this.props.selectedSubscription) {
            this.props.dispatch(getSubscriptions());
        }
    }

    onSubmit(e) {
        e.preventDefault();
        console.log('change dirs to: ', this.select.value);
        this.props.dispatch(selectSubscription(this.select.value));
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
                    ref={this.selectRef}>
                      {options}
                </select> 
                <button type='submit' onClick={(e) => this.onSubmit(e)}>Submit</button>             
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

export default connect(mapStateToProps)(Dashboard);

