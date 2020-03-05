import React, {useEffect, useState} from "react";
import {getMeal, getSchoolByCode, getMealDetailStat, getMealMenuStat} from "./api";

//import "./Meal.css";

import {withRouter} from "react-router-dom";
import styled from "styled-components";

import ShadowedButton from "./CustomCSS";

import Menu from "./Menu";
import MealDetailStat from "./MealDetailStat";
import Details from "./Details";
import MealMenuStat from "./MealMenuStat";

import Loading from "./Loading";
import useDebounce from "./useDebounce";




// const ShadowedButton = styled.button`
//     border: 1px solid #c4c4c4;
//   border-radius: 15px;
//
//   box-shadow:  0 3px 6px rgba(0,0,0,0.1);
//   cursor : pointer;
// `


const Container = styled.div`
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 20px;
  margin-bottom : 30px;
`

const Menus = styled.ul`
  margin: 0 auto;
  display: grid;
  padding-top: 20px;
  padding-bottom: 20px;
  width: 100%;
  grid-gap: 10px;
  cursor:pointer;
`

const InputDate = styled.input`
    font-size:17px;
    border: 1px solid #c4c4c4;
  border-radius: 15px;
 margin : 0 7px;
  padding: 3px 10px;
  box-shadow:  0 3px 6px rgba(0,0,0,0.1);
  width: 190px;
  background:#fff url(https://cdn1.iconfinder.com/data/icons/cc_mono_icon_set/blacks/16x16/calendar_2.png)  97% 50% no-repeat ;
  &::-webkit-inner-spin-button {
  display: none;
   }
   &::-webkit-calendar-picker-indicator {
  opacity: 0;
  }

  &::-webkit-clear-button
{
    display: none; /* Hide the button */
    -webkit-appearance: none; /* turn off default browser styling */
}
`

const SchoolName = styled.div`
    font-size : 24px;
`

const IndexButton = styled(ShadowedButton)`
    width : 80%;
    background-color : white;
    border : 1px solid #bbb;
    font-size : 14px;
    height : 28px;
    border-radius : 50px;
    margin-bottom : 15px;
`

const PrevButton = styled(ShadowedButton)`
background-color : white;
    border : 1px solid #bbb;
    font-size : 14px;
    height : 28px;
    border-radius : 50px;
    padding-left : 8px;
    padding-right : 8px;
`
const NextButton = styled(ShadowedButton)`
background-color : white;
    border : 1px solid #bbb;
    font-size : 14px;
    height : 28px;
    border-radius : 50px;
    padding-left : 8px;
    padding-right : 8px;
`

const Form = styled.div`
  display: flex;
  flex-flow: row wrap;
  align-items: center;
`

const MealData = styled.div`
width:80%
`

const MealStat = styled.div`
width:80%
`


const Meal = (props) => {

    const {params} = props.match;
    const [schoolName, setSchoolName] = useState("학교를 불러오는 중..");

    const GetMealMenuStatHandler = async (menu) => {
        function pad(n, width) {
            n = n + '';
            return n.length >= width ? n : new Array(width - n.length + 1).join('0') + n;
        }

        let now = new Date()
        let year = now.getFullYear()
        let month = now.getMonth() + 1

        let startDate, lastDate
        if (month == 1) {
            lastDate = String(year - 1) + "12"
            startDate = String(year - 1) + "01"
        } else {
            lastDate = String(year) + String(pad(month - 1, 2))
            startDate = String(year - 1) + String(pad(month, 2))
        }

        let query = {
            schoolCode: params.schoolCode,
            startDate: startDate,
            lastDate: lastDate,
            menu: menu
        }


        const response = await getMealMenuStat(query);
        console.log(response)
        if (response.status !== 404) {
            let data = response.data
            console.log("1111111111!!", data)
            setMenuStat(data)
        } else {
            props.history.push(`/`);
        }


    };

    const GetSchoolByCodeHandler = async (query) => {

        const response = await getSchoolByCode(query);
        console.log(response)
        if (response.status !== 404) {
            let data = response.data
            console.log("!!", data)
            if (data.schoolName !== params.schoolName) {
                props.history.push(`/meals/${params.schoolCode}/${data.schoolName}`);

            }
            setSchoolName(data.schoolName)
        } else {
            props.history.push(`/`);
        }


    };


    console.log("Params", params)

    let targetDate = "2019-12-19"

    const [date, setDate] = useState(targetDate);


    useEffect(() => {
        GetSchoolByCodeHandler(params.schoolCode)
        GetMealDetailStatHandler()
        GetMealMenuStatHandler()
    }, []);


    const [meals, setMeals] = useState([]);

    const [isLoading, setIsLoading] = useState(true);

    const [detailStat, setDetailStat] = useState();
    const [menuStat, setMenuStat] = useState();

    const debouncedDate = useDebounce(date, 250);


    function formatDate(date) {
        return date.replace(/-/gi, "")
    }


    useEffect(() => {
        GetMealHttpHandler({"date": formatDate(date), "type": "day"});
    }, [debouncedDate]);


    // text 검색어가 바뀔 때 호출되는 함수.
    const onDateUpdate = e => {
        console.log("SDF")
        setDate(e.target.value);
    };


    const moveSearchPage = () => {
        props.history.push(`/search/${params.schoolName}`);
    };

    const prevDate = () => {
        let temp = new Date(date);
        temp.setDate(temp.getDate() + parseInt(-1));
        temp = temp.toISOString().substring(0, 10);
        setDate(temp)

    }
    const nextDate = () => {
        let temp = new Date(date);
        temp.setDate(temp.getDate() + parseInt(1));
        temp = temp.toISOString().substring(0, 10);
        setDate(temp)
    }

    const moveDate = (date) => {
        setDate(date)
    }


    const GetMealHttpHandler = async (query) => {

        console.log("getMealHttp")

        // const params = {
        //   query: query,
        //   sort: "accuracy", // accuracy | recency 정확도 or 최신
        //   page: 1, // 페이지번호
        //   size: 10 // 한 페이지에 보여 질 문서의 개수
        // };
        const data = {
            schoolCode: params.schoolCode,
            date: query.date,
            type: query.type
        }
        setMeals([])
        setIsLoading(true)
        const response = await getMeal(data);
        setIsLoading(false)
        console.log(response)
        if (response.status !== 404) {
            let data = response.data.data
            setMeals(data);
        } else {
            setMeals([])
        }


    };

    const GetMealDetailStatHandler = async () => {

        function pad(n, width) {
            n = n + '';
            return n.length >= width ? n : new Array(width - n.length + 1).join('0') + n;
        }

        let now = new Date()
        let year = now.getFullYear()
        let month = now.getMonth() + 1

        let startDate, lastDate
        if (month == 1) {
            lastDate = String(year - 1) + "12"
            startDate = String(year - 1) + "01"
        } else {
            lastDate = String(year) + String(pad(month - 1, 2))
            startDate = String(year - 1) + String(pad(month, 2))
        }

        let query = {
            schoolCode: params.schoolCode,
            startDate: startDate,
            lastDate: lastDate
        }
        console.log("CCCCC", query)

        let running = 1;
        while (running) {
            const response = await getMealDetailStat(query);

            if (response !== "timeout") {
                if (response.status !== 404) {
                    let data = response.data
                    console.log("@@@@@@@@@@@@@@2", data)
                    setDetailStat(data.data)


                } else {

                }
                running = 0
            }
            console.log("response", response)
        }


    };


    return (
        <Container>


            <IndexButton
                onClick={moveSearchPage}
            >학교 검색으로..</IndexButton>
            <hr/>

            <SchoolName>{schoolName}</SchoolName>


            {date}의 급식

            <Form>
                <PrevButton onClick={prevDate}>◁</PrevButton>

                <InputDate
                    type="date"
                    name="date"
                    onChange={onDateUpdate} // change

                    value={date}
                />

                <NextButton onClick={nextDate}>▷</NextButton>
            </Form>


            <MealData>
                <Loading loading={isLoading}/>
                {(meals && meals.meal && meals.meal.length > 0) ?
                    (
                        <React.Fragment>
                            <Menus>

                                {meals.meal.map((menu, index) => (
                                    <Menu
                                        onClick={detailStat && (() => GetMealMenuStatHandler(menu))}
                                        key={index}
                                        menuName={menu}
                                    />
                                ))}

                            </Menus>

                            <Details data={meals.detail}/>

                        </React.Fragment>
                    )
                    :
                    (
                        <React.Fragment>
                            {!isLoading &&
                            <div>
                                급식을 찾을 수 없어요 ㅠ
                            </div>
                            }
                        </React.Fragment>

                    )

                }


            </MealData>
            <MealMenuStat data={menuStat}/>


            <br/>

            <MealStat>
                <MealDetailStat
                    data={detailStat}
                    moveDate={moveDate}
                />
            </MealStat>

        </Container>
    );
};
//aaasad
export default withRouter(Meal);
