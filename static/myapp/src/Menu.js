import React from "react";

import styled from 'styled-components';

import {withRouter} from "react-router-dom";

const MenuName = styled.li`
    text-align:center;
  list-style-type : none;
  border : 0.8px solid #eee;
  padding: 5px 20px;
`



const Menu = props => {

    return (
        <MenuName onClick={props.onClick}>
            {props.menuName}
        </MenuName>
    )
};

export default withRouter(Menu);
