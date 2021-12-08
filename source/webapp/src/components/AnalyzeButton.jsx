import React, { Component } from "react";
import Button from "react-bootstrap/Button"
import Modal from 'react-bootstrap/Modal'
import { Spinner } from 'react-bootstrap';
import { Badge } from "react-bootstrap";
import { ExclamationCircleFill, CheckCircleFill, QuestionCircleFill} from 'react-bootstrap-icons';

class AnalyzeButton extends Component {

  state = {
    isDialogOpen: false,
    analyzeStatus: {
      analyze_start_time: null,
      analyze_finish_time: null,
      analyze_status: 'not analyzed',
      failure_reason: ""
    }
  }

  componentDidMount() {
    const api = process.env.REACT_APP_API_ENDPOINT + '/analyze-status'
    fetch(api)
      .then(res => res.json())
        .then((data) => {
          this.setState({analyzeStatus: data })
        }).catch(console.log)
        
        if (this.isAnalyzeRunning()) {
            const thisBoundedAnalyzePoller = this.analyzePoller.bind(this)
            this.intervalId = setInterval(thisBoundedAnalyzePoller, 5000)
        }
  }

  analyzePoller() {
    const api = process.env.REACT_APP_API_ENDPOINT + '/analyze-status'
    fetch(api)
      .then(res => res.json())
        .then((data) => {
          this.setState({ analyzeStatus: data})
          console.log(data)
          if (!this.isAnalyzeRunning()) {
            console.log("Clearing analyze interval")
            clearInterval(this.intervalId)
          }
        }).catch(console.log)
  }

  openModal = () => this.setState({ isDialogOpen: true });

  triggerAnalyzeAndClose = () => {
    const api = process.env.REACT_APP_API_ENDPOINT + '/analyze-emails'
    fetch(api)
      .then(() => {
          console.log("triggered analysis")
          const thisBoundedAnalyzerPoller = this.analyzePoller.bind(this)
          this.intervalId = setInterval(thisBoundedAnalyzerPoller, 5000)
          this.closeModal()
        }).catch(console.log)
  }

  closeModal = () => {
        this.setState({ isDialogOpen: false });        
  }

  isAnalyzeRunning() {
    console.log("in isAnalyzeRunning()")
    console.log(this.state.analyzeStatus)
    if (this.state.analyzeStatus.analyze_status === 'analyzing' || 
          this.state.analyzeStatus.analyze_status === 'pending') {
      return(true)
    }
    return(false)
  }

  didAnalyzeFail() {
    if (this.state.analyzeStatus.analyze_status === 'aborted' || 
    this.state.analyzeStatus.analyze_status === 'failed') {
      return(true)
    }
    return(false)
  }

  getTimeString(epcTime) {
    if (epcTime != null) {
      let fTime = new Date(epcTime * 1000)
      return fTime.toLocaleString()
    }
    return ""
  }

  isFirstTime() {
    if (this.state.analyzeStatus.analyze_status === 'not analyzed') {
      return(true)
    }
    return(false) 
  }

  render() {
    let buttonToReturn = null
    if (this.isAnalyzeRunning()) {
      buttonToReturn = 
          <Button variant="outline-success" onClick={this.openModal} disabled>
          <Spinner
            as="span"
            animation="border"
            size="sm"
            role="status"
            aria-hidden="true"
          /> Analyze Emails
          <span className="visually-hidden">Analyze Emails</span>
        </Button>
    } else {
      let status = null
      if (this.didAnalyzeFail()) {
        status = <ExclamationCircleFill color="red"/>
      } else if (this.isFirstTime()) {
        status = <QuestionCircleFill color="orange"/> 
      } else {
        status = <CheckCircleFill color="green"/>
      }

      buttonToReturn = 
        <Button variant="outline-success" onClick={this.openModal}>
        Analyze Emails {' '}
        {status}
        </Button>
    }

    let modalBody = null
    if (!this.didAnalyzeFail()) {
      modalBody = 
        <Modal.Body>
          <p>Last Analysis Started at: {this.getTimeString(this.state.analyzeStatus.analyze_start_time)}</p> 
          <p>Last Analysis Ended at: {this.getTimeString(this.state.analyzeStatus.analyze_finish_time)}</p> 
          <p>Analysis Status: <Badge bg="success">{this.state.analyzeStatus.analyze_status}</Badge></p>
        </Modal.Body>
    } else {
      modalBody = 
        <Modal.Body>
          <p>Last Analysis Started at: {this.getTimeString(this.state.analyzeStatus.analyze_start_time)}</p> 
          <p>Last Analysis Ended at: {this.getTimeString(this.state.analyzeStatus.analyze_finish_time)}</p> 
          <p>Analysis Status: <Badge bg="success">{this.state.analyzeStatus.analyze_status}</Badge></p>
          <p>Reason: {this.state.analyzeStatus.failure_reason}</p>
        </Modal.Body>
    }

    return (
      <React.Fragment>

        {buttonToReturn}

        <Modal show={this.state.isDialogOpen} onHide={this.closeModal}>
          <Modal.Header closeButton>
            <Modal.Title>Analyze Status</Modal.Title>
          </Modal.Header>
            {modalBody} 
          <Modal.Footer>            
            <Button variant="primary" onClick={this.triggerAnalyzeAndClose}>
             Analyze 
            </Button>
          </Modal.Footer>
        </Modal>
      </React.Fragment>      
    )
  }
}

export default AnalyzeButton