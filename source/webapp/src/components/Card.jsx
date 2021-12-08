import React from 'react'
import { useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";

function Card(props) {

  let navigate = useNavigate();

  const handleRoute = () => { 
    navigate("/list-emails", 
    {
      state: {
        topic: props.topic.topic
      }
    })
  }

  let topic_link = "list-emails?topic=" + props.topic.topic

  return (
    <div class="card">
      <h5 class="card-header">Topic: {props.topic.topic}</h5>
      <div class="card-body">
        <h6 class="card-subtitle mb-2 text-muted">Keywords: {props.topic.keywords.join(', ')}</h6>
        <br/>
        <div class="d-grid gap-4 d-md-flex">
          <Link to={topic_link}>
          <button class="btn btn-secondary btn-sm position-relative">
            All Messages
            <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
              {props.topic.total}
              <span class="visually-hidden">unread messages</span>
            </span>
          </button>
          </Link>

          <Link to={topic_link}>
          <button type="button" class="btn btn-primary btn-sm position-relative">
            Unread 
            <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
              {props.topic.unread}
              <span class="visually-hidden">unread messages</span>
            </span>
          </button>
          </Link>
        </div>
      </div>
    </div>
  )
}  

export default Card