import settings from './settings';

export function login(token) {
  localStorage.setItem('feedback_map-token', token);
}

export function logout() {
  localStorage.clear();
}

export function sessionRequest(url, options={}) {
  options.headers = options.headers || {};
  if (options && options.data && typeof options.data == 'object') {
    options.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(options.data);
  }
  try {
    const token = localStorage.getItem('feedback_map-token');
    if (token) {
      options.headers.Authorization = "Token " + token;
    }
  }
  catch (DOMException) {
    console.log('Local storage not accessible, proceeding as anonymous user.')
  }
  return fetch(settings.serverRoot + url, options);
}

export default sessionRequest;
