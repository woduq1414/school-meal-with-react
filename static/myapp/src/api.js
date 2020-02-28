import axios from "axios";

// const Kakao = axios.create({
//   baseURL: "https://dapi.kakao.com", // 공통 요청 경로를 지정해준다.
//   headers: {
//     Authorization: `KakaoAK 59218beddcaf075c5b745f560b6702a7` // 공통으로 요청 할 헤더
//   }
// });
//
// // search blog api
// export const blogSearch = params => {
//   return Kakao.get("/v2/search/blog", { params });
// };

const Kakao = axios.create({
    baseURL: process.env.baseURL || "http://127.0.0.1:5000/api", // 공통 요청 경로를 지정해준다.
});

// search blog api
export const blogSearch = params => {
    return Kakao.get(`/schools/${params}`)
        .then((response) => {
            // Success 🎉
            // console.log(response.data);
            return response;
        })
        .catch((error) => {
            // Error 😨
            if (error.response) {
                /*
                 * The request was made and the server responded with a
                 * status code that falls out of the range of 2xx
                 */
                // console.log(error.response.data);
                // console.log(error.response.status);
                // console.log(error.response.headers);
                return error.response


            } else if (error.request) {
                /*
                 * The request was made but no response was received, `error.request`
                 * is an instance of XMLHttpRequest in the browser and an instance
                 * of http.ClientRequest in Node.js
                 */
                console.log(error.request);
            } else {
                // Something happened in setting up the request and triggered an Error
                console.log('Error', error.message);
            }
            // console.log(error.config);
        });
    ;

};