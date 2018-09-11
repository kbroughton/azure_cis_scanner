import {normalizeResponseErrors} from './utils';

export const GET_DIRS_REQUEST = 'GET_DIRS_REQUEST';
export const getDirsRequest = data => ({
    type: GET_DIRS_REQUEST,
    data
});

export const GET_DIRS_SUCCESS = 'GET_DIRS_SUCCESS';
export const getDirsSuccess = data => ({
    type: GET_DIRS_SUCCESS,
    data
});

export const GET_DIRS_ERROR = 'GET_DIRS_ERROR';
export const getDirsError = error => ({
    type: GET_DIRS_ERROR,
    error
});

export const SELECT_DIR_REQUEST = 'SELECT_DIR_REQUEST';
export const selectDirRequest = error => ({
    type: SELECT_DIR_REQUEST,
    error
});
export const SELECT_DIR_SUCCESS = 'SELECT_DIR_SUCCESS';
export const selectDirSuccess = data => ({
    type: SELECT_DIR_SUCCESS,
    data
});

export const SELECT_DIR_ERROR = 'SELECT_DIR_ERROR';
export const selectDirError = error => ({
    type: SELECT_DIR_ERROR,
    error
});

export const SET_SELECTED_DIR = 'SET_SELECTED_DIR';
export const setSelectedDir = dir => ({
    type: SET_SELECTED_DIR,
    dir
})

export const getDirs = () => (dispatch) => {
    return fetch(`http://localhost:5000/`, {
        method: 'GET'
    })
        .then(res => normalizeResponseErrors(res))
        .then(res => res.json())
        .then(data =>  {
            console.log(data);
            dispatch(getDirsSuccess(data))
        })
        .catch(err => dispatch(getDirsError(err)));
};

export const selectDir = (dir) => (dispatch) => {
    console.log(dir)
    dispatch(setSelectedDir(dir));
    return fetch(`http://localhost:5000/${dir}`, {
        method: 'POST',
        body: JSON.stringify({
            dir
        })
    })
    .then(res => normalizeResponseErrors(res))
    .then(res => res.json())
    .then(data => dispatch(selectDirSuccess(data)))
    .catch(err => dispatch(selectDirError(err)));
}