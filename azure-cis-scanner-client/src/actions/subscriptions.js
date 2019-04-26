import { normalizeResponseErrors } from "./utils";

export const SET_SERVICE = "SET_SERVICE";
export const setService = data => ({
  type: SET_SERVICE,
  data
});

export const SET_STAT_VIS = "SET_STAT_VIS";
export const showStat = data => ({
  type: SET_STAT_VIS,
  data
});

export const GET_SUBSCRIPTIONS_REQUEST = "GET_SUBSCRIPTIONS_REQUEST";
export const getSubscriptionsRequest = data => ({
  type: GET_SUBSCRIPTIONS_REQUEST,
  data
});

export const GET_SUBSCRIPTIONS_SUCCESS = "GET_SUBSCRIPTIONS_SUCCESS";
export const getSubscriptionsSuccess = data => ({
  type: GET_SUBSCRIPTIONS_SUCCESS,
  data
});

export const GET_SUBSCRIPTIONS_ERROR = "GET_SUBSCRIPTIONS_ERROR";
export const getSubscriptionsError = error => ({
  type: GET_SUBSCRIPTIONS_ERROR,
  error
});

export const SELECT_SUBSCRIPTION = "SELECT_SUBSCRIPTION";
export const selectSubscription = data => ({
  type: SELECT_SUBSCRIPTION,
  data
});

export const SELECT_SERVICE_REQUEST = "SELECT_SERVICE_REQUEST";
export const selectServiceRequest = error => ({
  type: SELECT_SERVICE_REQUEST,
  error
});
export const SELECT_SERVICE_SUCCESS = "SELECT_SERVICE_SUCCESS";
export const selectServiceSuccess = data => ({
  type: SELECT_SERVICE_SUCCESS,
  data
});

export const SELECT_SERVICE_ERROR = "SELECT_SERVICE_ERROR";
export const selectServiceError = error => ({
  type: SELECT_SERVICE_ERROR,
  error
});

export const GET_CIS_REQUEST = "GET_CIS_REQUEST";
export const getCisRequest = error => ({
  type: GET_CIS_REQUEST,
  error
});
export const GET_CIS_SUCCESS = "GET_CIS_SUCCESS";
export const getCisSuccess = data => ({
  type: GET_CIS_SUCCESS,
  data
});

export const GET_CIS_ERROR = "GET_CIS_ERROR";
export const getCisError = error => ({
  type: GET_CIS_ERROR,
  error
});

export const getSubscriptions = () => dispatch => {
  return fetch(`http://localhost:5000/subscription_tuples`)
    .then(res => normalizeResponseErrors(res))
    .then(res => res.json())
    .then(data => {
      let dataArray = [""];
      // create subscription dir from tuples
      for (let i = 0; i < data.length; i++) {
        let subscription_dir =
          data[i][2].split(" ").join("-") + "-" + data[i][0].split("-")[0];
        dataArray.push(subscription_dir);
      }
      dispatch(getSubscriptionsSuccess(dataArray));
    })
    .catch(err => dispatch(getSubscriptionsError(err)));
};

// get cis structure for nav
export const getCis = () => dispatch => {
  return fetch(`http://localhost:5000/cis_structure`)
    .then(res => normalizeResponseErrors(res))
    .then(res => res.json())
    .then(data => {
      dispatch(getCisSuccess(data));
    })
    .catch(err => dispatch(getCisError(err)));
};

export const selectService = service => dispatch => {
  return fetch(`http://localhost:5000/services/${service}`)
    .then(res => normalizeResponseErrors(res))
    .then(res => res.json())
    .then(data => {
      console.log(data);
      dispatch(selectServiceSuccess(data));
    })
    .catch(err => dispatch(selectServiceError(err)));
};
