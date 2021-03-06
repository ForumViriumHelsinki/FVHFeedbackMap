import React from "react";
import CenteredSpinner from "util_components/bootstrap/CenteredSpinner";

export default class LoadScreen extends React.Component {
  render() {
    return <div className="container">
      <div className="jumbotron mt-5 bg-light shadow text-center">
        <img className="w-50" src="images/FORUM_VIRIUM_logo_orange.png"/>
        <h3>FVH Feedback Map</h3>
        <p className="lead text-primary mt-3">To confidently go where many a delivery man has gotten lost
          before.</p>
        <CenteredSpinner/>
      </div>
    </div>;
  }
}
