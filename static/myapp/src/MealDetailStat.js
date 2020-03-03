import React from "react";

import styled from 'styled-components';
import {Tab, Tabs, TabList, TabPanel} from 'react-tabs';
import 'react-tabs/style/react-tabs.css';

import {withRouter} from "react-router-dom";
import Item from "./Item";

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


const MealDetailStat = props => {

    function formatDate(date) {
        return `${date.substring(0, 4)}-${date.substring(4, 6)}-${date.substring(6, 8)}`
    }

    console.log(props.data)
    if (props.data) {
        return (
            <React.Fragment>
                <h2>
                    지난 1년 간 급식 영양 통계
                </h2>
                <Tabs style={{"textAlign": "center"}}>
                    <TabList>
                        {
                            Object.keys(props.data).map((key, index) => (
                                <Tab>{key}</Tab>
                            ))
                        }

                    </TabList>
                    {
                        Object.keys(props.data).map((key, index) => (
                            <TabPanel>
                                <ul>
                                    <Li>
                                        <LeftSpan>지난 1년 중 가장 {key}가 높았던 날은?</LeftSpan>
                                        <RightSpan
                                            onClick={() => props.moveDate(formatDate(props.data[key].max.date))}>{formatDate(props.data[key].max.date)}
                                            ({props.data[key].max.value})
                                        </RightSpan>
                                    </Li>
                                    <Li>
                                        <LeftSpan>지난 1년 중 가장 {key}가 낮았던 날은?</LeftSpan>
                                        <RightSpan
                                            onClick={() => props.moveDate(formatDate(props.data[key].min.date))}>{formatDate(props.data[key].min.date)}
                                            ({props.data[key].min.value})
                                        </RightSpan>
                                    </Li>
                                    <Li>
                                        <LeftSpan>지난 1년 동안의 평균 {key}는?</LeftSpan>
                                        <RightSpan>
                                            {props.data[key].average}
                                        </RightSpan>
                                    </Li>
                                </ul>

                            </TabPanel>
                        ))
                    }


                </Tabs>
            </React.Fragment>

        )
    } else {
        return <React.Fragment/>
    }

};


export default withRouter(MealDetailStat);
