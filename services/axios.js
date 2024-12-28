import axios from "axios";
import { useUserStore } from "@/stores/user";

const axiosInstance = axios.create({
    baseURL: "http://localhost:8000", // Replace with your FastAPI backend URL
    withCredentials: true,
});

// Add a request interceptor. If user not authenticated, redirect to login page
// const loginRedirectInterceptor = axios.interceptors.response.use(
//     (response) => {}, 
//     (error) => {
//     if (error.status === 401) {
//         nuxtApp.router.push("/login"); //TODO: fix to actual functionality for login
//     }
// });

// Add a request interceptor. If user authenticated, add session_id to request headers THIS SHOULD BE DONE IN THE STORE INSTEAD
// const authInterceptor = axios.interceptors.request.use((config) => {
//     userStore = useUserStore();
//     if (userStore.isAuthenticated()) {
//         config.headers.session_id = userStore.session_id;
//     }
// });

// Add a request interceptor which redirects request if loggedIn
let user_redirect_routes = {
    "/search": "/user/search",
    "/explore": "/user/explore",
    "/recommendations": "/user/recommendations",
}
const userRerouteInterceptor = axios.interceptors.request.use((config) => {
    userStore = useUserStore();
    if (userStore.isAuthenticated()) {
        if (user_redirect_routes[config.url]) {
            config.url = user_redirect_routes[config.url];
        }
    }
});

// Add a response interceptor. If response has a message, show it as a toast
const responseToastInterceptor = axios.interceptors.response.use(
    // (response) => {
    //     if (response.data.message) {
    //         nuxtApp.$toast.success(response.data.message);
    //     }
    // },
    (error) => {
        if (!error.status) {
            nuxtApp.$toast.error('Network Error');
        } else {
            nuxtApp.$toast.error(`Error: ${error.status}`);
        }
        return Promise.reject(error);
    }
);


// Cancel duplicate requests
const pendingRequests = new Map();

const duplicateReqInterceptor = axios.interceptors.request.use((config) => {
    const requestKey = `${config.method}:${config.url}`;
    if (pendingRequests.has(requestKey)) {
        const cancel = pendingRequests.get(requestKey);
        cancel();
    }
    config.cancelToken = new axios.CancelToken((cancel) => {
        pendingRequests.set(requestKey, cancel);
    });
});

const duplicateRespInterceptor = axios.interceptors.response.use((response) => {
    const requestKey = `${response.config.method}:${response.config.url}`;
    pendingRequests.delete(requestKey);
}, (error) => {
    const requestKey = `${error.config.method}:${error.config.url}`;
    pendingRequests.delete(requestKey);
    return Promise.reject(error);
});

export default axiosInstance;
