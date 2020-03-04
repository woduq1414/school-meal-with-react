import React from "react";

import styled from 'styled-components';


import {withRouter} from "react-router-dom";
import {Tab} from "react-tabs";

const LeftSpan = styled.div`
    text-align:center;

  border-right : 0.8px solid #eee;
  width : 50%;
  font-size : 18px;
  display:inline-block;
`

const RightSpan = styled.div`
    text-align:center;


  width : 50%;
  font-size : 18px;
    display:inline-block;
    cursor:pointer;
`

const Li = styled.li`
list-style-type : none;
    text-align : center;
`


const MealMenuStat = props => {

    function formatDate(date) {
        return `${date.substring(0, 4)}-${date.substring(4, 6)}-${date.substring(6, 8)}`
    }

    function sortObject(o) {

        return Object.keys(o).sort((a, b) => {
                        return o[a] - o[b]
                    }).reduce((prev, curr, i) => {
                        prev[i] = o[curr]
                        return prev
                    }, {});


    }


    console.log(props.data)
    let data = props.data

    if (data) {
        return (
            <React.Fragment>
                <h2>
                    지난 1년 간 급식 메뉴 통계
                </h2>
                <h3>
                    {data.days}일의 급식들 중에..
                </h3>
                <ul style={{"height" : "200px", "overflow-y" : "scroll", "width" : "80%", "text-align" : "center"}}>


                {
                    Object.keys(data.data).map((key, index) => (
                        <li>{data.data[key][0]} : {data.data[key][1]}회</li>
                    ))
                }

                </ul>
            </React.Fragment>

        )
    } else {
        return (
            <React.Fragment>
                <h2>
                    지난 1년 간 급식 메뉴 통계
                </h2>
                {/*급식 메뉴를 클릭해보세요!*/}
            </React.Fragment>
        )
    }

};


export default withRouter(MealMenuStat);
