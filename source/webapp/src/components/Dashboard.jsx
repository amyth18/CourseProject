import React from "react";
import { Component } from "react";
import { Row } from 'react-bootstrap';
import { Col } from 'react-bootstrap';
import Card from './Card';
import NavBar from './navbar';

class Dashboard extends Component {

  state = {
    topics: []
  }

  componentDidMount() {
    const api = process.env.REACT_APP_API_ENDPOINT + '/topic-summary'
    fetch(api)
    .then(res => res.json())
    .then((data) => {
      this.setState({ topics: data })
    }).catch(console.log)
  }

  render() {
    return (  
      <React.Fragment>
      <NavBar />
      <main className="container">
      <Row xs={1} md={2} className="g-4">
      { 
        this.state.topics.map((topic) => {
            return (
              <Col>
                <Card topic={topic}/>
              </Col>
            )
          })
      }
      </Row>
      </main>
    </React.Fragment> 
    )
  }  
}

export default Dashboard