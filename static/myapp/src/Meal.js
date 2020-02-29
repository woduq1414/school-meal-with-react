import React, {useEffect, useState} from "react";
import {getMeal} from "./api";

//import "./Meal.css";

import {withRouter} from "react-router-dom";
import styled from "styled-components";

import ShadowedButton from "./CustomCSS";

import Menu from "./Menu";
import Details from "./Details";
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
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 20px;
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


const Meal = (props) => {

    console.log(props)

    const {params} = props.match;
    console.log(props)

    let targetDate = "2019-12-19"

    const [date, setDate] = useState(targetDate);

    const [meals, setMeals] = useState([]);

    const [isLoading, setIsLoading] = useState(true);
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

    return (
        <Container>


            <IndexButton
                onClick={moveSearchPage}
            >학교 검색으로..</IndexButton>
            <hr/>

            <SchoolName>{params.schoolName}</SchoolName>


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
                                급식이 없어요 ㅠ
                            </div>
                            }
                        </React.Fragment>

                    )

                }
                {/*{!meals.meal && !isLoading &&*/}
                {/*    <div>*/}
                {/*        급식 어디갔찌*/}
                {/*    </div>*/}
                {/*}*/}


            </MealData>


        </Container>
    );
};
//aa
export default withRouter(Meal);
