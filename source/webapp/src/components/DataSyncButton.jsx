import React, { Component } from "react";
import Button from "react-bootstrap/Button"
import Modal from 'react-bootstrap/Modal'
import { Spinner } from 'react-bootstrap';
import { Badge } from "react-bootstrap";
import { ExclamationCircleFill, CheckCircleFill, QuestionCircleFill} from 'react-bootstrap-icons';

class DataSyncButton extends Component {

  state = {
    isDialogOpen: false,
    dataSyncStatus: {
      sync_start_time: null,
      sync_finish_time: null,
      sync_status: 'not synced',
      downloaded: 0,
      failure_reason: ""
    }
  }

  componentDidMount() {
    const api = process.env.REACT_APP_API_ENDPOINT + '/data-sync-status'
    fetch(api)
      .then(res => res.json())
        .then((data) => {
          this.setState({dataSyncStatus: data })
        }).catch(console.log)
        
        if (this.isDataSyncRunning()) {
            const thisBoundedDataSyncPoller = this.dataSyncPoller.bind(this)
            this.intervalId = setInterval(thisBoundedDataSyncPoller, 5000)
        }
  }

  dataSyncPoller() {
    const api = process.env.REACT_APP_API_ENDPOINT + '/data-sync-status'
    fetch(api)
      .then(res => res.json())
        .then((data) => {
          this.setState({ dataSyncStatus: data})          
          if (!this.isDataSyncRunning()) {
            console.log("Clearing interval")
            clearInterval(this.intervalId)
          }
        }).catch(console.log)
  }

  openModal = () => this.setState({ isDialogOpen: true });

  triggerSyncAndClose = () => {
    const api = process.env.REACT_APP_API_ENDPOINT + '/data-sync'
    fetch(api)
      .then(() => {
          console.log("triggered data sync")
          const thisBoundedDataSyncPoller = this.dataSyncPoller.bind(this)
          this.intervalId = setInterval(thisBoundedDataSyncPoller, 5000)
          this.closeModal()
        }).catch(console.log)
  }

  closeModal = () => {
        this.setState({ isDialogOpen: false });        
  }

  isDataSyncRunning() {
    if (this.state.dataSyncStatus.sync_status === 'syncing' || 
          this.state.dataSyncStatus.sync_status === 'pending') {
      return(true)
    }
    return(false)
  }

  didDataSyncFail() {
    if (this.state.dataSyncStatus.sync_status === 'aborted' || 
    this.state.dataSyncStatus.sync_status === 'failed') {
      return(true)
    }
    return(false)
  }

  isFirstTime() {
    if (this.state.dataSyncStatus.sync_status === 'not synced') {
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

  render() {
    let buttonToReturn = null
    if (this.isDataSyncRunning()) {
      buttonToReturn = 
          <Button variant="outline-success" onClick={this.openModal} disabled>
          <Spinner
            as="span"
            animation="border"
            size="sm"
            role="status"
            aria-hidden="true"
          /> Sync Emails 
          <Badge bg="primary">{this.state.dataSyncStatus.downloaded}</Badge>
          <span className="visually-hidden">unread messages</span>
        </Button>
    } else {
      let status = null
      if (this.didDataSyncFail()) {
        status = <ExclamationCircleFill color="red"/>
      } else if (this.isFirstTime()) {
        status = <QuestionCircleFill color="orange"/> 
      } else {
        status = <CheckCircleFill color="green"/>
      }
      buttonToReturn = 
        <Button variant="outline-success" onClick={this.openModal}>
          Sync Emails{' '}
          {status}
          <span className="visually-hidden">unread messages</span>
        </Button>
    }

    let modalBody = null
    if (!this.didDataSyncFail()) {
      modalBody = 
        <Modal.Body>
          <p>Last Sync Started at: {this.getTimeString(this.state.dataSyncStatus.sync_start_time)}</p> 
          <p>Last Sync Ended at: {this.getTimeString(this.state.dataSyncStatus.sync_finish_time)}</p> 
          <p>Sync Status: <Badge bg="success">{this.state.dataSyncStatus.sync_status}</Badge></p>
          <p>Total Emails Downloaded: {this.state.dataSyncStatus.downloaded}</p>
        </Modal.Body>
    } else {
      modalBody = 
        <Modal.Body>
          <p>Last Sync Started at: {this.getTimeString(this.state.dataSyncStatus.sync_start_time)}</p> 
          <p>Last Sync Ended at: {this.getTimeString(this.state.dataSyncStatus.sync_finish_time)}</p> 
          <p>Sync Status: <Badge bg="success">{this.state.dataSyncStatus.sync_status}</Badge></p>
          <p>Reason: {this.state.dataSyncStatus.failure_reason}</p>
        </Modal.Body>
    }

    return (
      <React.Fragment>

        {buttonToReturn}

        <Modal show={this.state.isDialogOpen} onHide={this.closeModal}>
          <Modal.Header closeButton>
            <Modal.Title>Data Sync Status</Modal.Title>
          </Modal.Header>
            {modalBody} 
          <Modal.Footer>            
            <Button variant="primary" onClick={this.triggerSyncAndClose}>
              Sync
            </Button>
          </Modal.Footer>
        </Modal>
      </React.Fragment>      
    )
  }
}

export default DataSyncButton