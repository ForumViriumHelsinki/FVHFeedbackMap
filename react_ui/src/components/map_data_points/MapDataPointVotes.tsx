import React from 'react';
// @ts-ignore
import {Button, ButtonGroup} from 'reactstrap';
import {AppContext, MapDataPoint} from "components/types";
import Icon from "util_components/bootstrap/Icon";
import sessionRequest from "sessionRequest";
import {downvoteMapDataPointUrl, upvoteMapDataPointUrl} from "urls";

type MapDataPointVotesProps = {
  mapDataPoint: MapDataPoint,
  onUpdate: (note: MapDataPoint) => any
}

export default class MapDataPointVotes extends React.Component<MapDataPointVotesProps> {
  static contextType = AppContext;

  buttonProps = {
    outline: true,
    size: 'sm',
    className: 'btn-compact'
  };

  render() {
    const {mapDataPoint} = this.props;
    const upvoteUrl = upvoteMapDataPointUrl(mapDataPoint.id as number);
    const downvoteUrl = downvoteMapDataPointUrl(mapDataPoint.id as number);

    return <ButtonGroup className="btn-block">
      <Button {...this.buttonProps} color="success" onClick={()=> this.updateNote(upvoteUrl)}>
        <Icon icon="thumb_up"/> Useful ({mapDataPoint.upvotes ? mapDataPoint.upvotes.length : 0})
      </Button>
      <Button {...this.buttonProps} color="danger" onClick={()=> this.updateNote(downvoteUrl)}>
        <Icon icon="thumb_down"/> Not useful ({mapDataPoint.downvotes ? mapDataPoint.downvotes.length : 0})
      </Button>
    </ButtonGroup>;
  }

  updateNote = (url: string) => {
    const {onUpdate} = this.props;

    sessionRequest(url, {method: 'PUT'}).then(response => {
      if (response.status < 400) response.json().then((note: MapDataPoint) => onUpdate(note))
    })
  };
}
