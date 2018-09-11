import React from 'react';
import {connect} from 'react-redux';
import {getDirs, selectDir} from '../actions/dashboard';

class Dashboard extends React.Component {
    constructor(props) {
        super(props);
       
        this.select;
        this.selectRef = select => {
            this.select = select
        }
    }

    componentDidMount() {
        if (!this.props.selectedDir) {
            this.props.dispatch(getDirs());
        }
    }

    onSubmit(e) {
        e.preventDefault();
        console.log('change dirs to: ', this.select.value);
        this.props.dispatch(selectDir(this.select.value));
    }

    render() {
        const {dirs} = this.props;
        let options;
        let selected;
       
        if (this.props.dirs) {
            options = dirs.map((dir, index) => {
                let selected;
                console.log(this.props.selectedDir, dir)
                if (this.props.selectedDir === dir.id) {
                    selected = "selected"
                }
                return <option key={index} selected={selected} value={dir.id}>{dir.name}</option>
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
    
    return {
      dirs: state.dirs.dirs,
      selectedDir: state.dirs.selectedDir
    };
};

export default connect(mapStateToProps)(Dashboard);

