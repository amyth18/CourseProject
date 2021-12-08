import React from "react";
import { Component } from "react";
import NavBar from './navbar';
import Emails from "./Emails";

class EmailsPage extends Component {

  componentDidMount() {

  }

  render() {
    return (
      <React.Fragment>
        <NavBar />
        <Emails />
      </React.Fragment> 
    )
  }  
}

export default EmailsPage