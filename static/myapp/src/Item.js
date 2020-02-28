import React from "react";

import styled from 'styled-components';

import {withRouter} from "react-router-dom";

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

    const onClick = e => {
        props.history.push(`/meals/${props.schoolCode}/${props.schoolName}`, {"aa" : "bb"});
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
