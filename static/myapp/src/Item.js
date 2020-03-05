import React from "react";

import styled from 'styled-components';
import {InsertSchoolNow} from "./api";
import {withRouter} from "react-router-dom";

import NProgress from "nprogress/nprogress"
import "nprogress/nprogress.css"


const School = styled.li`
  list-style-type : none;
  border : 0.8px solid #eee;
  padding: 5px 20px;
`

const Upper = styled.dl`
  margin-bottom : 10px;
`

const Under = styled.dl`
`

const SchoolName = styled.span`
vertical-align:middle;
`
const SchoolCode = styled.span`
vertical-align:middle;
color : gray;
font-size : 0.7em;
`


const Item = props => {
    const InsertSchoolNowHandler = async () => {
        NProgress.start()
        const response = await InsertSchoolNow({"schoolCode":props.schoolCode, "schoolName":props.schoolName});
        if (response.status !== 404) {
            props.history.push(`/meals/${props.schoolCode}/${props.schoolName}`);
        } else {
            props.history.push(`/`);
        }
        NProgress.done()
    }
    const onClick = e => {

        InsertSchoolNowHandler()

    };


    return (
        <School onClick={onClick}>
            <Upper>
                <SchoolName>{props.schoolName} · </SchoolName>
                <SchoolCode>{props.schoolCode}</SchoolCode>
            </Upper>
            <Under>{props.schoolAddress}</Under>
        </School>
    )
};

export default withRouter(Item);
