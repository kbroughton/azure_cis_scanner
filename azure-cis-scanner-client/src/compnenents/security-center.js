import React from 'react';
import {connect} from 'react-redux';
import {Redirect} from 'react-router-dom';

class SecurityCenter extends React.Component {
    

    // componentDidMount() {
        
    // }

    // onSubmit(e) {
       
    // }

    render() {
        if (!this.props.selectedDir) {
            return <Redirect to='/' />
        }
        return (
            <div>
                <p>The current directory is {this.props.selectedDir}</p>
            </div>
        );
    }
}

const mapStateToProps = state => {
    
    return {
      subscriptions: state.subscriptions.subscriptions,
      selectedSubscription: state.subscriptions.selectedSubscription
    };
};

export default connect(mapStateToProps)(SecurityCenter);