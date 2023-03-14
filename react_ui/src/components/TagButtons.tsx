import React from 'react';
import sessionRequest from "sessionRequest";
import {mapDataPointsUrl} from "urls";
import {MapDataPoint, Tag} from "components/types";
import Geolocator from "util_components/Geolocator";
import {Location} from "util_components/types";
import MapDataPointModal from "components/map_data_points/MapDataPointModal";
import {getTags} from "components/map_data_points/utils";

type TagButtonsProps = {}

type TagButtonsState = {
  tags?: Tag[],
  currentPosition?: Location,
  dataPoint?: MapDataPoint
}

const initialState: TagButtonsState = {};

export default class TagButtons extends React.Component<TagButtonsProps, TagButtonsState> {
  state = initialState;

  componentDidMount() {
    getTags.then(tags => this.setState({tags}));
  }

  render() {
    const {} = this.props;
    const {tags, dataPoint} = this.state;
    const maxHeight = !tags ? 0 : Math.round(40 / tags.length) + 'vh';
    return !tags ? '' : <div className="container-fluid" style={{height: '100%'}}>
      <Geolocator onLocation={([lon, lat]) => this.setState({currentPosition: {lat, lon}})}/>
      <div className="row" style={{height: '100%'}}>
        {tags.map(({tag, icon, color}) =>
          <div className="col-6 d-flex" key={tag}>
            <button className={`btn btn-${color} mb-3 mt-3 btn-block btn-lg`} onClick={() => this.newPoint(tag)}>
              {icon && <><img src={icon} style={{maxHeight, maxWidth: 480}}/><br/></>}
              {tag}
            </button>
          </div>)}
      </div>
      {dataPoint && <MapDataPointModal onClose={() => this.setState({dataPoint: undefined})} note={dataPoint}/>}
    </div>;
  }

  newPoint(tag: string) {
    const {currentPosition} = this.state;
    if (!currentPosition) return;
    const {lat, lon} = currentPosition;
    sessionRequest(mapDataPointsUrl, {method: 'POST', data: {lat, lon, tags: [tag]}})
    .then(response => response.json())
    .then((dataPoint) => this.setState({dataPoint}))
  }
}
