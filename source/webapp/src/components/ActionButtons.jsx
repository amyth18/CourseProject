import { Component } from "react";
import Button from "react-bootstrap/Button"

class ActionButtons extends Component {
  
  render() {
    return (
      <>
        <Button variant="outline-primary">Sync Emails</Button>{' '} 
        <Button variant="outline-primary">Analyze Emails</Button>{' '} 
      </>
    )
  }
}

export default ActionButtons