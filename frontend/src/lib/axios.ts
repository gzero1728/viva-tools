import axios from "axios";

// API base URL 설정
const API_BASE_URL = import.meta.env.VITE_API_URL;

// axios 인스턴스 생성 및 설정
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// 요청 인터셉터
axiosInstance.interceptors.request.use(
  (config) => {
    // 요청 전에 수행할 작업
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터
axiosInstance.interceptors.response.use(
  (response) => {
    // 응답 데이터 가공이 필요한 경우
    return response;
  },
  (error) => {
    // 에러 처리
    return Promise.reject(error);
  }
);

export default axiosInstance;
