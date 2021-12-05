import React, { Component } from 'react';
import DataSyncButton from './DataSyncButton';
import AnalyzeButton from './AnalyzeButton';

class Settings extends Component {

  render() {
    
    return (
      <React.Fragment>
        <DataSyncButton />
        <AnalyzeButton />
      </React.Fragment>
    );
  }
}

export default Settings;

