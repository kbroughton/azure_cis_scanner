import {
  SET_SERVICE,
  SET_STAT_VIS,
  GET_SUBSCRIPTIONS_REQUEST,
  GET_SUBSCRIPTIONS_SUCCESS,
  GET_SUBSCRIPTIONS_ERROR,
  SELECT_SUBSCRIPTION,
  SELECT_SERVICE_ERROR,
  SELECT_SERVICE_REQUEST,
  SELECT_SERVICE_SUCCESS,
  GET_CIS_ERROR,
  GET_CIS_REQUEST,
  GET_CIS_SUCCESS
} from "../actions/subscriptions";

const initialState = {
  subscriptions: "",
  selectedSubscription: "",
  selectedServiceData: null,
  service: null,
  finding: null,
  stats: null,
  showStat: false,
  error: null,
  loading: false,
  nav: null
};

export default function reducer(state = initialState, action) {
  if (action.type === SET_SERVICE) {
    return {
      ...state,
      service: action.data
    };
  } else if (action.type === SET_STAT_VIS) {
    return {
      ...state,
      showStat: action.data
    };
  } else if (action.type === GET_SUBSCRIPTIONS_REQUEST) {
    return {
      ...state,
      loading: true
    };
  } else if (action.type === GET_SUBSCRIPTIONS_SUCCESS) {
    return {
      ...state,
      loading: false,
      subscriptions: action.data,
      selectedSubscription: action.data.active_subscription_dirs,
      error: null
    };
  } else if (action.type === GET_SUBSCRIPTIONS_ERROR) {
    return {
      ...state,
      loading: false,
      error: action.error
    };
  } else if (action.type === SELECT_SUBSCRIPTION) {
    return {
      ...state,
      selectedSubscription: action.data
    };
  } else if (action.type === SELECT_SERVICE_REQUEST) {
    return {
      ...state,
      loading: true
    };
  } else if (action.type === SELECT_SERVICE_SUCCESS) {
    console.log(action.data.stats);
    return {
      ...state,
      loading: false,
      finding: action.data.findings_table,
      stats: action.data.stats,
      service: action.data.service
    };
  } else if (action.type === SELECT_SERVICE_ERROR) {
    return {
      ...state,
      loading: false,
      error: action.error
    };
  } else if (action.type === GET_CIS_REQUEST) {
    return {
      ...state,
      loading: true
    };
  } else if (action.type === GET_CIS_SUCCESS) {
    return {
      ...state,
      loading: false,
      nav: action.data.section_ordering
    };
  } else if (action.type === GET_CIS_ERROR) {
    return {
      ...state,
      loading: false,
      error: action.error
    };
  }
  return state;
}
