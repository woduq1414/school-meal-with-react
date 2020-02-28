import React, {useEffect, useState} from "react";
import {blogSearch} from "./api";

import "./App.css";
import Item from "./Item";

import {withRouter} from "react-router-dom";

const App = props => {
    const {params} = props.match;
    const keyword = params.keyword || "";

    const [blogs, setBlogs] = useState([]);
    const [text, setText] = useState(keyword);
    // const [query, setQuery] = useState(keyword);

    useEffect(() => {
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

        const response = await blogSearch(query);
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
        <div className="container">
            <input
                type="search"
                placeholder="검색어를 입력 하세요..."
                name="query"
                className="input_search"
                onKeyDown={onEnter} // enter
                onChange={onTextUpdate} // change
                value={text} // view
            />

            <ul>
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
            </ul>
        </div>
    );
};
//aa
export default withRouter(App);
