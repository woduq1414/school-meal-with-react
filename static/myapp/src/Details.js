import React from "react";

import styled from 'styled-components';

import {withRouter} from "react-router-dom";

const DetailName = styled.th`
    text-align:center;
  list-style-type : none;
  border : 0.8px solid #eee;
  padding: 5px 20px;
   @media only screen and (max-width: 760px), (min-device-width: 768px) and (max-device-width: 1024px)  {
        display: block;
    }
`

const DetailValue = styled.td`
    text-align:center;
  list-style-type : none;
  border : 0.8px solid #eee;
  padding: 5px 20px;
  @media only screen and (max-width: 760px), (min-device-width: 768px) and (max-device-width: 1024px)  {
        display: block;
        \tborder: none;
\t\t\tborder-bottom: 1px solid #eee;
\t\t\tposition: relative;
\t\t\tpadding-left: 50%;
&:before {
    \tposition: absolute;
\t\t\t/* Top/left values mimic padding */
\t\t\ttop: 0;
\t\t\tleft: 6px;
\t\t\twidth: 45%;
\t\t\tpadding-right: 10px;
\t\t\twhite-space: nowrap;
   ${(props) => props.detailName &&`
   content : "${props.detailName}"
  `}
}
    }
`

const DetailTable = styled.table`
    width : 100%;
    @media only screen and (max-width: 760px), (min-device-width: 768px) and (max-device-width: 1024px)  {
        display: block;
    }
`
const Thead = styled.thead`
@media only screen and (max-width: 760px), (min-device-width: 768px) and (max-device-width: 1024px)  {
        display: block;
    }
`
const TheadTr = styled.tr`
@media only screen and (max-width: 760px), (min-device-width: 768px) and (max-device-width: 1024px)  {
        display: block;
        position: absolute;
top: -9999px;
left: -9999px;
    margin: 0 0 1rem 0;
    }
`
const TbodyTr = styled.tr`
@media only screen and (max-width: 760px), (min-device-width: 768px) and (max-device-width: 1024px)  {
        display: block;
    margin: 0 0 1rem 0;
    }
`


const Tbody = styled.tbody`
@media only screen and (max-width: 760px), (min-device-width: 768px) and (max-device-width: 1024px)  {
        display: block;
    }
`





const Details = props => {

    return (
        <DetailTable>
            <Thead>
                <TheadTr>
                    {Object.keys(props.data).map((detailName, index) => (
                        <DetailName>{detailName}</DetailName>
                    ))}
                </TheadTr>


            </Thead>
            <Tbody>
                <TbodyTr>
                    {Object.keys(props.data).map((detailName, index) => (
                        <DetailValue detailName={detailName}>{props.data[detailName]}</DetailValue>
                    ))}

                </TbodyTr>

            </Tbody>
        </DetailTable>
    )
};

export default Details;
