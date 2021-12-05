import React, { Component } from 'react'
import Settings from './SettingsModal'

class NavBar extends Component {
  render() {
    return (
      <nav className="navbar navbar-light bg-light">
        <div className="container-fluid">
          <span className="navbar-brand mb-0 h1">GMail Inbox</span>
          <form className="d-flex">
            <Settings />
          </form>
        </div>
      </nav>
    )
  }
}

export default NavBar