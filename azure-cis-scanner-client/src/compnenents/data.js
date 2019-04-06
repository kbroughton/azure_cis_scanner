import React from 'react';
import { Route } from 'react-router-dom';
import {connect} from 'react-redux';
import { bindActionCreators } from 'redux';
import Dashboard from './dashboard';
import { selectService } from '../actions/subscriptions';

class DisplayData extends React.Component {
    constructor(props) {
        super(props);
            this.state = {
                dataList: true,
                findingList: false,
            }
        }
    
    

    componentDidMount() {
        const { service, selectedSubscription } = this.props;
        if (!service || !selectedSubscription) {
            console.log('return to dashboard')
            return <Route exact path='/subscriptions' component={Dashboard} />
        } else {
            this.props.selectService(service);
        }
    }

    render() {
        let dataList;
        const { finding, data, selectedSubscription } = this.props;

        if (finding) {
            console.log('render findings ', finding)
        } else if (!data) {
            dataList = "";
        } else {
            dataList = data.map((data, index) => {
            return <li className='data' key={index.toString()}><span className='standard'>{data[0]}: </span>{data[1]}</li>
            })
        }
        return (
            <React.Fragment>
                <h3>Current Directory is {selectedSubscription}</h3>
                <ul>
                    {dataList}
                </ul>
            </React.Fragment>
        );
    }
}

const mapStateToProps = state => {
    
    return {
      data: state.subscriptions.selectedServiceData,
      subscriptions: state.subscriptions.subscriptions,
      service: state.subscriptions.service,
      finding: state.subscriptions.finding,
      selectedSubscription: state.subscriptions.selectedSubscription
    };
};

export default connect(
    mapStateToProps,
    dispatch => bindActionCreators({ selectService }, dispatch),
    )(DisplayData);