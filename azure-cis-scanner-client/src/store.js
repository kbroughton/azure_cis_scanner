import {createStore, applyMiddleware, combineReducers, compose} from 'redux';
import thunk from 'redux-thunk';
import subscriptionReducer from './reducers/subscriptions';

const middlewares = [ thunk ];
const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;

const store = createStore(
    combineReducers({
        subscriptions: subscriptionReducer
    }),
    composeEnhancers(
        applyMiddleware(...middlewares)
    )
);

export default store;