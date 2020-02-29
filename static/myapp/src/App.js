import React, {useEffect, useState} from "react";
import {blogSearch} from "./api";

import styled, { createGlobalStyle }  from 'styled-components';

import './App.css'

import Loading from "./Loading";
import Item from "./Item";

import {withRouter} from "react-router-dom";

import useDebounce from "./useDebounce";

// const GlobalStyle = createGlobalStyle`
//   @import url("https://fonts.googleapis.com/css?family=Noto+Sans+KR&display=swap");
//
// * {
//   font-family: "Noto Sans KR", sans-serif;
//   box-sizing: border-box;
//   padding: 0;
//   margin: 0;
// }
//
// html,
// body {
//   height: 100%;
// }
// `;




const InputSearch = styled.input`

  font-family: "Noto Sans KR", sans-serif;
  font-size: 18px;
  border: 0;
  border-bottom: 1px solid #dddddd;
  width: 80%;
  padding: 20px;
  display: block;
  transition: border 0.3s;
  &:focus {
     outline: none;
    border-bottom: 1px solid #0675f3;
  }
`

const Container = styled.div`
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 50px;
`

const Schools = styled.ul`
  display: grid;
  padding-top: 20px;
  padding-bottom: 20px;
  width: 80%;
  grid-gap: 10px;
  cursor:pointer;
`


const App = props => {
    const {params} = props.match;
    const keyword = params.keyword || "";

    const [blogs, setBlogs] = useState([]);
    const [isLoading, setIsLoading] = useState(keyword);
    const [text, setText] = useState(keyword);

    // const [query, setQuery] = useState(keyword);

    useEffect(() => {
        console.log("SFD")
        if (keyword.length > 0) {
            blogSearchHttpHandler(keyword, true);
        } else {
            setBlogs([]);
        }
    }, [keyword]);

    // 엔터를 눌렀을 때 호출 되는 함수
    const onEnter = e => {
        if (e.keyCode === 13) {
            if (text.length === 0) props.history.push(`/`);
            else props.history.push(`/search/${text}`);
        }
    };

    // text 검색어가 바뀔 때 호출되는 함수.
    const onTextUpdate = e => {
        setText(e.target.value);
    };

    const blogSearchHttpHandler = async (query, reset) => {
        // const params = {
        //   query: query,
        //   sort: "accuracy", // accuracy | recency 정확도 or 최신
        //   page: 1, // 페이지번호
        //   size: 10 // 한 페이지에 보여 질 문서의 개수
        // };
        setBlogs([])
        setIsLoading(true)

        const response = await blogSearch(query);
        setIsLoading(false)
        console.log(response)
        if(response.status !== 404){
            let data = response.data;
            if (reset) {
                setBlogs(data);
            } else {
                setBlogs(blogs.concat(data));
            }
        }else{
            setBlogs([])
        }



    };

    return (

        <Container>


            <InputSearch
                type="text"
                placeholder="검색어를 입력 하세요..."
                name="query"
                onKeyDown={onEnter} // enter
                onChange={onTextUpdate} // change
                value={text} // view
            />

            <Schools>
                {/*{isLoading ? <Loading loading={isLoading}/> : ""}*/}
                <Loading loading={isLoading}/>
                {blogs.length == 100 &&
                    <div>※ 해당 결과가 너무 많아 가나다 순 상위 100개만 보여집니다.</div>
                }

                {blogs.map((blog, index) => (
                    <Item
                        key={index}
                        schoolType={blog.schoolType}
                        schoolRegion={blog.schoolRegion}
                        schoolAddress={blog.schoolAddress}
                        schoolName={blog.schoolName}
                        schoolCode={blog.schoolCode}
                    />
                ))}
            </Schools>
        </Container>
    );
};
//aa
export default withRouter(App);
