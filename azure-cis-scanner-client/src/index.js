import React from 'react';
import ReactDOM from 'react-dom';
import {BrowserRouter as Router} from 'react-router-dom';
import {Provider} from 'react-redux';
import store from './store';
import './index.css';
import App from './compnenents/App';
import registerServiceWorker from './registerServiceWorker';

ReactDOM.render( 
<Provider store={store}>
    <Router>
        <App />
    </Router>
</Provider>, document.getElementById('root'));
registerServiceWorker();
