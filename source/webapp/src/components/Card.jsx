import React, { Component } from 'react'

class Card extends Component {

  state = {
    topic : this.props.topic
  }

  render() {
    const href = "/list-emails?topic=" + this.state.topic.topic
    return (
      <div class="card">
        <h5 class="card-header">Topic: {this.state.topic.topic}</h5>
        <div class="card-body">
          <h6 class="card-subtitle mb-2 text-muted">Keywords: {this.state.topic.keywords.join(', ')}</h6>
          <br/>
          <div class="d-grid gap-4 d-md-flex">
            <a class="btn btn-secondary btn-sm position-relative" href={href}>
              All Messages
              <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                {this.state.topic.total}
                <span class="visually-hidden">unread messages</span>
              </span>
            </a>

            <button type="button" class="btn btn-primary btn-sm position-relative">
            Unread 
              <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                {this.state.topic.unread}
                <span class="visually-hidden">unread messages</span>
              </span>
            </button>
          </div>
        </div>
      </div>
    )
  }
}

export default Card