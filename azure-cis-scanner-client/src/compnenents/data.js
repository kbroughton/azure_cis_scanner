import React from 'react';
import {connect} from 'react-redux';
import { bindActionCreators } from 'redux';
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
        const { service } = this.props;
        this.props.selectService(service);
    }

    render() {
        let dataList;
        const { finding, data } = this.props;

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
            <ul>
                {dataList}
            </ul>
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