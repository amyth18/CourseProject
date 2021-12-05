import './App.css';
import React, {Component} from 'react';
import { Row } from 'react-bootstrap';
import { Col } from 'react-bootstrap';
import Card from './components/Card';
import NavBar from './components/navbar';

class App extends Component {

  state = {
    topics: []
  }

  componentDidMount() {
    
    fetch('http://localhost:8080/topic-summary')
    .then(res => res.json())
    .then((data) => {
      this.setState({ topics: data })
    }).catch(console.log)

    //this.setState({topics: [{
    //  topic: "Topic A",
    //  total: 100,
    //  unread: 50,
    //  keywords: ['word1']
    //}]})
  }

  render() {
    console.log(this.state.topics)
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

export default App;
