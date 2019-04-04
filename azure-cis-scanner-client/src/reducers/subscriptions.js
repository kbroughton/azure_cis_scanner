import {
    SET_SERVICE,
    GET_SUBSCRIPTIONS_REQUEST,
    GET_SUBSCRIPTIONS_SUCCESS,
    GET_SUBSCRIPTIONS_ERROR,
    SELECT_SUBSCRIPTION_REQUEST,
    SELECT_SUBSCRIPTION_SUCCESS,
    SELECT_SUBSCRIPTION_ERROR,
    SELECT_SERVICE_ERROR,
    SELECT_SERVICE_REQUEST,
    SELECT_SERVICE_SUCCESS
} from '../actions/subscriptions';

const initialState = {
    subscriptions: "",
    selectedSubscription: "",
    selectedServiceData: null,
    service: null,
    finding: null,
    error: null,
    loading: false
};

export default function reducer(state = initialState, action) {
    if (action.type === SET_SERVICE) {
        return {
            ...state,
            service: action.data
        }
    } else if (action.type === GET_SUBSCRIPTIONS_REQUEST) {
        return {
            ...state,
            loading: true
        } 
    } else if (action.type === GET_SUBSCRIPTIONS_SUCCESS) {
        return {
            ...state,
            loading: false,
            subscriptions: action.data,
            selectedSubscription: action.data.active_subscription_dirs,
            error: null
        }
    } else if (action.type === GET_SUBSCRIPTIONS_ERROR) {
        return {
            ...state,
            loading: false,
            error: action.error
        }
    } else if (action.type === SELECT_SUBSCRIPTION_REQUEST) {
        return {
            ...state,
            loading: true
        }
     } else if (action.type === SELECT_SUBSCRIPTION_SUCCESS) {
        return {
            ...state,
            loading: false,
            selectedSubscription: action.data.active_subscription_dir
        }
    } else if (action.type === SELECT_SUBSCRIPTION_ERROR) {
        return {
            ...state,
            loading: false,
            error: action.error
        }
    } else if (action.type === SELECT_SERVICE_REQUEST) {
        return {
            ...state,
            loading: true
        }
     } else if (action.type === SELECT_SERVICE_SUCCESS) {
        return {
            ...state,
            loading: false,
            selectedServiceData: action.data.findings_table
        }
    } else if (action.type === SELECT_SERVICE_ERROR) {
        return {
            ...state,
            loading: false,
            error: action.error
        }
    } 
    return state;
}
