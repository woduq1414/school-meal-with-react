import React from "react";

const Item = props => {
    // return (
    //   <li>
    //     <dl>
    //       <dt>
    //         <img src={props.thumbnail} alt={props.thumbnail} />
    //       </dt>
    //       <dd>
    //         <h3 dangerouslySetInnerHTML={{ __html: props.title }} />
    //         <p>{props.blogname}</p>
    //         <article dangerouslySetInnerHTML={{ __html: props.contents }} />
    //         <a href={props.url} target="_blank">
    //           링크 바로가기
    //         </a>
    //       </dd>
    //     </dl>
    //   </li>
    // );
    return (
        <li className={"school"}>
            <dl className={"upper"}>
                <span className={"schoolName"}>{props.schoolName} · </span>
                <span className={"schoolCode"}>{props.schoolCode}</span>
            </dl>
            <dl className={"under"}>{props.schoolAddress}</dl>
        </li>
    )
};

export default Item;
