import {
    GET_SUBSCRIPTIONS_REQUEST,
    GET_SUBSCRIPTIONS_SUCCESS,
    GET_SUBSCRIPTIONS_ERROR,
    SELECT_SUBSCRIPTION_REQUEST,
    SELECT_SUBSCRIPTION_SUCCESS,
    SELECT_SUBSCRIPTION_ERROR,
    SET_SELECTED_SUBSCRIPTION,
    SELECT_SERVICE_ERROR,
    SELECT_SERVICE_REQUEST,
    SELECT_SERVICE_SUCCESS
} from '../actions/subscriptions';

const initialState = {
    subscriptions: null,
    selectedSubscriptionData: null,
    selectedServiceData: null,
    error: null,
    selectedSubscription: "",
    loading: false
};

export default function reducer(state = initialState, action) {
    if (action.type === GET_SUBSCRIPTIONS_REQUEST) {
        return {
            ...state,
            loading: true
        } 
    }else if (action.type === GET_SUBSCRIPTIONS_SUCCESS) {
        return {
            ...state,
            loading: false,
            subscriptions: action.data.subscriptions,
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
            selectedSubscriptionData: action.data
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
            selectedSubscriptionData: action.data
        }
    } else if (action.type === SELECT_SERVICE_ERROR) {
        return {
            ...state,
            loading: false,
            error: action.error
        }
    } else if (action.type === SET_SELECTED_SUBSCRIPTION) {
        console.log(action.dir)
        return {
            ...state,
            selectedSubscription: action.dir
        }
    }
    return state;
}
