import React from 'react';
import {connect} from 'react-redux';
import {Redirect} from 'react-router-dom';

class LoggingAndMonitoring extends React.Component {
    

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
                <p>The current directory is {this.props.selectedDir.name} {this.props.selectedDir}</p>

            </div>
        );
    }
}

const mapStateToProps = state => {
    
    return {
      dirs: state.dirs.dirs,
      selectedDir: state.dirs.selectedDir
    };
};

export default connect(mapStateToProps)(LoggingAndMonitoring);