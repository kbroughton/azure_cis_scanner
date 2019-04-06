import {normalizeResponseErrors} from './utils';

export const SET_SERVICE = 'SET_SERVICE';
export const setService = data => ({
    type: SET_SERVICE,
    data
})

export const GET_SUBSCRIPTIONS_REQUEST = 'GET_SUBSCRIPTIONS_REQUEST';
export const getSubscriptionsRequest = data => ({
    type: GET_SUBSCRIPTIONS_REQUEST,
    data
});

export const GET_SUBSCRIPTIONS_SUCCESS = 'GET_SUBSCRIPTIONS_SUCCESS';
export const getSubscriptionsSuccess = data => ({
    type: GET_SUBSCRIPTIONS_SUCCESS,
    data
});

export const GET_SUBSCRIPTIONS_ERROR = 'GET_SUBSCRIPTIONS_ERROR';
export const getSubscriptionsError = error => ({
    type: GET_SUBSCRIPTIONS_ERROR,
    error
});

export const SELECT_SUBSCRIPTION_REQUEST = 'SELECT_SUBSCRIPTION_REQUEST';
export const selectSubscriptionRequest = error => ({
    type: SELECT_SUBSCRIPTION_REQUEST,
    error
});
export const SELECT_SUBSCRIPTION_SUCCESS = 'SELECT_SUBSCRIPTION_SUCCESS';
export const selectSubscriptionSuccess = data => ({
    type: SELECT_SUBSCRIPTION_SUCCESS,
    data
});

export const SELECT_SUBSCRIPTION_ERROR = 'SELECT_SUBSCRIPTION_ERROR';
export const selectSubscriptionError = error => ({
    type: SELECT_SUBSCRIPTION_ERROR,
    error
});

export const SELECT_SERVICE_REQUEST = 'SELECT_SERVICE_REQUEST';
export const selectServiceRequest = error => ({
    type: SELECT_SERVICE_REQUEST,
    error
});
export const SELECT_SERVICE_SUCCESS = 'SELECT_SERVICE_SUCCESS';
export const selectServiceSuccess = data => ({
    type: SELECT_SERVICE_SUCCESS,
    data
});

export const SELECT_SERVICE_ERROR = 'SELECT_SERVICE_ERROR';
export const selectServiceError = error => ({
    type: SELECT_SERVICE_ERROR,
    error
});


export const getSubscriptions = () => (dispatch) => {
    return fetch(`http://localhost:5000/subscription_tuples`, {
        method: 'GET',
        mode: 'cors'
    })
        .then(res => normalizeResponseErrors(res))
        .then(res => res.json())
        .then(data => {
            let dataArray = [""];
            // create subscription dir from tuple
            for (let i = 0; i < data.length; i++) {
                let subscription_dir = data[i][2]
                    .split(" ")
                    .join("-") + "-" + data[i][0]
                    .split("-")[0] 
                dataArray.push(subscription_dir)
            };
            console.log("subscriptions = ", dataArray)
            dispatch(getSubscriptionsSuccess(dataArray))})
        .catch(err => dispatch(getSubscriptionsError(err)));
};

export const selectSubscription = (subscription) => (dispatch) => {
    console.log(subscription)
    return fetch(`http://localhost:5000/subscriptions/${subscription}`, {
        mode: 'cors',
        headers: {'Access-Control-Allow-Origin': '*'}
    })
        .then(res => normalizeResponseErrors(res))
        .then(res => res.json())
        .then(data =>  {
            console.log("data", data);
            dispatch(selectSubscriptionSuccess(data))
        })
        .catch(err => dispatch(selectSubscriptionError(err)));
}

export const selectService = (service) => (dispatch) => {
    console.log(service)
    return fetch(`http://localhost:5000/services/${service}`, {
        mode: 'cors',
        headers: {'Access-Control-Allow-Origin': '*'}
    })
        .then(res => normalizeResponseErrors(res))
        .then(res => res.json())
        .then(data => {
            console.log(data);
            dispatch(selectServiceSuccess(data))})
        .catch(err => dispatch(selectServiceError(err)));
}