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
    baseURL: (window.location.hostname == "127.0.0.1" || window.location.hostname == "localhost") ? "http://127.0.0.1:5000/api" : "https://school-meal-with-react.herokuapp.com/api", // 공통 요청 경로를 지정해준다.  process.env.baseURL ||
});

// search blog api
export const blogSearch = params => {
    console.log()
    return Kakao.get(`/schools/name/${params}`)
        .then((response) => {

            return response;
        })
        .catch((error) => {
            // Error 😨
            if (error.response) {

                return error.response


            } else if (error.request) {

                console.log(error.request);
            } else {

                console.log('Error', error.message);
            }
        });
    ;

};

export const InsertSchoolNow = params => {
    console.log()
    return Kakao.get(`/schools/name/${params.schoolName}?now=true&schoolCode=${params.schoolCode}`)
        .then((response) => {

            return response;
        })
        .catch((error) => {
            // Error 😨
            if (error.response) {

                return error.response


            } else if (error.request) {

                console.log(error.request);
            } else {

                console.log('Error', error.message);
            }
        });
    ;

};

export const getSchoolByCode = params => {
    console.log()
    return Kakao.get(`/schools/code/${params}`)
        .then((response) => {

            return response;
        })
        .catch((error) => {
            // Error 😨
            if (error.response) {

                return error.response


            } else if (error.request) {

                console.log(error.request);
            } else {

                console.log('Error', error.message);
            }
        });
    ;

};


export const getMeal = params => {
    console.log(`/meals/${params.schoolCode}/day/${params.date}`)
    return Kakao.get(`/meals/${params.schoolCode}/day/${params.date}`)
        .then((response) => {

            return response;
        })
        .catch((error) => {
            // Error 😨
            if (error.response) {

                return error.response


            } else if (error.request) {

                console.log(error.request);
            } else {

                console.log('Error', error.message);
            }
        });
    ;

};


export const getMealDetailStat = params => {
    console.log("SDFFFFFFFFFFFFFFFFFFF")
    return Kakao.get(`/meals/stat/detail/${params.schoolCode}?startDate=${params.startDate}&lastDate=${params.lastDate}`)
        .then((response) => {

            return response;
        })
        .catch((error) => {
            // Error 😨
            if (error.response) {

                return error.response


            } else if (error.request) {

                console.log("request", error.request);

                return "timeout"
            } else {

                console.log('Error', error.message);
            }
        });
    ;

};


export const getMealMenuStat = params => {
    console.log("SDFFFFFFFFFFFFFFFFFFF")
    return Kakao.get(`/meals/stat/menu/${params.schoolCode}/${btoa(encodeURIComponent(params.menu))
    }?startDate=${params.startDate}&lastDate=${params.lastDate}`)
        .then((response) => {

            return response;
        })
        .catch((error) => {
            // Error 😨
            if (error.response) {

                return error.response


            } else if (error.request) {

                console.log("request", error.request);

                return "timeout"
            } else {

                console.log('Error', error.message);
            }
        });
    ;

};