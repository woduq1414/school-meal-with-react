import React from "react";
import { BrowserRouter, Route, Switch } from "react-router-dom";
import App from "./App";
import Meal from "./Meal";

const Client = props => {
  return (
    <BrowserRouter>
      <Switch>
        <Route path="/search/:keyword" component={App} />
        <Route exact path="/" component={App} />
        <Route exact path="/meals/:schoolCode/:schoolName" component={Meal} />
      </Switch>
    </BrowserRouter>
  );
};

export default Client;
