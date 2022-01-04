import React from 'react';
import {AppContext, MapDataPoint} from "components/types";
import {formatTimestamp} from "utils";
import sessionRequest from "sessionRequest";
import {mapDataPointCommentsUrl, mapDataPointCommentUrl} from "urls";
import ErrorAlert from "util_components/bootstrap/ErrorAlert";
import Icon from "util_components/bootstrap/Icon";

type MapDataPointCommentsProps = {
  mapDataPoint: MapDataPoint,
  refreshNote: () => any
}

type MapDataPointCommentsState = {
  error: boolean,
  changed: boolean
}

const initialState: MapDataPointCommentsState = {
  error: false,
  changed: false
};

export default class MapDataPointComments extends React.Component<MapDataPointCommentsProps> {
  state = initialState;
  static contextType = AppContext;

  render() {
    const {mapDataPoint, refreshNote} = this.props;
    const {error, changed} = this.state;
    const {user} = this.context;
    const comments = mapDataPoint.comments || [];

    return <div className="m-2 ml-3">
      <p>
        <strong>Comments ({(comments || []).length}) </strong>
        <button className="btn btn-light btn-sm btn-compact float-right" onClick={refreshNote}>
          <Icon icon={'refresh'}/>
        </button>
      </p>

      {comments.map(comment =>
        <div key={comment.id} className="mb-2 mt-2">
          <strong>{comment.user || 'Anonymous'} {formatTimestamp(comment.created_at)}:</strong>
          {user && user.is_reviewer &&
            <button className="btn btn-light btn-compact btn-discrete p-0 ml-1"
                    onClick={() => this.onDelete(comment.id)}>
              <Icon icon="delete_outline"/>
            </button>
          }
          <br/>
          {comment.comment}
        </div>
      )}
      <ErrorAlert message="Commenting failed. Try again maybe?" status={error}/>
      <textarea className="form-control" placeholder="Write your comment here" id="new-comment"
                onChange={() => this.setState({changed: true})}/>
      <button className={"btn btn-primary btn-block" + (changed ? '' : ' invisible')} onClick={this.submit}>Submit</button>
    </div>;
  }

  submit = () => {
    const {mapDataPoint, refreshNote} = this.props;
    const commentEl = document.getElementById('new-comment') as HTMLTextAreaElement;
    const data = {map_data_point: mapDataPoint.id, comment: commentEl.value};
    sessionRequest(mapDataPointCommentsUrl, {method: 'POST', data}).then(response => {
      if (response.status >= 400) this.setState({error: true});
      else {
        this.setState({error: false, changed: false});
        commentEl.value = '';
        refreshNote();
      }
    })
  };

  onDelete = (commentId: number) => {
    const {refreshNote} = this.props;

    sessionRequest(mapDataPointCommentUrl(commentId), {method: 'DELETE'}).then(response => {
      if (response.status >= 400) this.setState({error: true});
      else {
        this.setState({error: false});
        refreshNote();
      }
    })
  };
}
