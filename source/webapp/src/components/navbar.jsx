import React, { Component } from 'react'
import Settings from './SettingsModal'
import { Navbar } from 'react-bootstrap'
import { Container } from 'react-bootstrap'

class MyNavBar extends Component {
  render() {
    return (
      <Navbar bg="light" expand="lg">
        <Container>
          <Navbar.Brand href="/">Gmail Inbox</Navbar.Brand>
          <form className="d-flex">
            <Settings />
          </form>
        </Container>
      </Navbar>
    )
  }
}

export default MyNavBar