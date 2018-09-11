import {createStore, applyMiddleware, combineReducers} from 'redux';
import thunk from 'redux-thunk';
import dirsReducer from './reducers/dirs';

const store = createStore(
    combineReducers({
        dirs: dirsReducer
    }),
    applyMiddleware(thunk)
);

export default store;