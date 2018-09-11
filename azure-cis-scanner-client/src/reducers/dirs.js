import {
    GET_DIRS_REQUEST,
    GET_DIRS_SUCCESS,
    GET_DIRS_ERROR,
    SELECT_DIR_REQUEST,
    SELECT_DIR_SUCCESS,
    SELECT_DIR_ERROR,
    SET_SELECTED_DIR
} from '../actions/dashboard';

const initialState = {
    dirs: null,
    selectedDirData: null,
    error: null,
    selectedDir: null,
    loading: false
};

export default function reducer(state = initialState, action) {
    if (action.type === GET_DIRS_REQUEST) {
        return {
            ...state,
            loading: true
        } 
    }else if (action.type === GET_DIRS_SUCCESS) {
        return {
            ...state,
            loading: false,
            dirs: action.data.dirs,
            error: null
        }
    } else if (action.type === GET_DIRS_ERROR) {
        return {
            ...state,
            loading: false,
            error: action.error
        }
    } else if (action.type === SELECT_DIR_REQUEST) {
        return {
            ...state,
            loading: true
        }
     } else if (action.type === SELECT_DIR_SUCCESS) {
        return {
            ...state,
            loading: false,
            selectedDirData: action.data
        }
    } else if (action.type === SELECT_DIR_ERROR) {
        return {
            ...state,
            loading: false,
            error: action.error
        }
    } else if (action.type === SET_SELECTED_DIR) {
        console.log(action.dir)
        return {
            ...state,
            selectedDir: action.dir
        }
    }
    return state;
}
