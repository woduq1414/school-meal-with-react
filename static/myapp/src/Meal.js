import React, {useEffect, useState} from "react";
import {getMeal} from "./api";

//import "./Meal.css";

import {withRouter} from "react-router-dom";
import styled from "styled-components";

import Menu from "./Menu";


const Container = styled.div`
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 20px;
`

const Menus = styled.ul`
  display: grid;
  padding-top: 20px;
  padding-bottom: 20px;
  width: 80%;
  grid-gap: 10px;
  cursor:pointer;
`

const InputDate = styled.input`
`

const SchoolName = styled.div`
    font-size : 24px;
`

const IndexButton = styled.button`
    width : 80%;
    background-color : white;
    border : 1px solid #bbb;
    font-size : 14px;
    height : 28px;
    border-radius : 50px;
    margin-bottom : 15px;
`

const PrevButton = styled.button`
background-color : white;
    border : 1px solid #bbb;
    font-size : 14px;
    height : 28px;
    border-radius : 50px;
    padding-left : 8px;
    padding-right : 8px;
`
const NextButton = styled.button`
background-color : white;
    border : 1px solid #bbb;
    font-size : 14px;
    height : 28px;
    border-radius : 50px;
    padding-left : 8px;
    padding-right : 8px;
`


const Meal = (props) => {

    console.log(props)

    const {params} = props.match;
    console.log(props)

    let targetDate = "2019-12-19"

    const [date, setDate] = useState(targetDate);

    const [meals, setMeals] = useState([]);

    function formatDate(date) {
        return date.replace(/-/gi, "")
    }


    useEffect(() => {
        GetMealHttpHandler({"date": formatDate(date), "type": "day"});
    }, [date]);


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

        const response = await getMeal(data);
        console.log(response)
        if (response.status !== 404) {
            let data = response.data.data.meal
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

            <PrevButton onClick={prevDate}>◁</PrevButton>

            <InputDate
                type="date"
                name="date"
                onChange={onDateUpdate} // change

                value={date}
            />

            <NextButton onClick={nextDate}>▷</NextButton>
            <Menus>
                {meals.map((menu, index) => (
                    <Menu
                        key={index}
                        menuName={menu}
                    />
                ))}

            </Menus>


        </Container>
    );
};
//aa
export default withRouter(Meal);
