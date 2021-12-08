import React, { Component } from "react";
import DataTable from 'react-data-table-component';

const columns = [
    {
        name: 'From',
        selector: row => row.from
    },
    {
        name: 'Subject',
        selector: row => row.subject
    },
    {
        name: 'Key Topics',
        selector: row => {
            if (row.email_topics == null) {
                return ""
            } else {
                row.email_topics.join(', ')
            }                
        }
    },
];

class Emails extends Component {
    state = {
        emails: []
      }
    
    componentDidMount() {
        let search = window.location.search;
        let params = new URLSearchParams(search);
        let topic = params.get('topic');
        fetch('http://localhost:8080/emails?topic=' + topic)
        .then(res => res.json())
        .then((data) => {
            this.setState({ emails: data })
        }).catch(console.log)
    }

  render() {
    return (
      <DataTable
          columns={columns}
          data={this.state.emails}
          pagination        
      />
    );
  }
}

export default Emails