import React from 'react';
import {withRouter} from "react-router-dom";
import _ from 'lodash';

import {MapDataPointsContext, MapDataPoint} from "components/types";
import {Location} from "util_components/types";
import MapDataPointFiltersButton from "components/map_data_points/MapDataPointFiltersButton";
import NotificationsButton from "components/map_data_points/NotificationsButton";
import NewMapDataPoint from "components/map_data_points/NewMapDataPoint";
import MapDataPointModal from "components/map_data_points/MapDataPointModal";
import MapDataPointsMap from "components/map_data_points/MapDataPointsMap";
import MapToolButton from "components/map_data_points/MapToolButton";

type MapDataPointsEditorProps = {
  history: any, // from withRouter
  location: any, // from withRouter
  match: any, // from withRouter
  selectedNoteId?: number,
  newNote?: boolean,
}

type MapDataPointsEditorState = {
  filters: any,
  selectLocation?: (location: any) => any,
  onLocationCancelled?: () => any,
  location?: Location
}

const initialState: () => MapDataPointsEditorState = () => ({
  filters: {}
});

class MapDataPointsEditor extends React.Component<MapDataPointsEditorProps, MapDataPointsEditorState> {
  state: MapDataPointsEditorState = initialState();

  static contextType = MapDataPointsContext;

  render() {
    const {newNote, selectedNoteId, history} = this.props;
    const {mapDataPoints, refreshNote, loadMapDataPoints} = this.context;
    const {filters, selectLocation, location} = this.state;

    const note = mapDataPoints && selectedNoteId &&
      (_.find(mapDataPoints, {id: selectedNoteId}) || {id: selectedNoteId} as MapDataPoint);

    return <div className="flex-grow-1">
      <div className="position-absolute map-tools p-3">
        <NewMapDataPoint requestNoteType={newNote}
                         requestLocation={this.requestLocation}
                         cancelLocationRequest={this.cancelLocationRequest} />

        {!selectLocation && <>
          <MapToolButton icon="refresh" onClick={loadMapDataPoints} />
          <MapDataPointFiltersButton mapDataPoints={mapDataPoints}
                                     onFiltersChanged={filters => this.setState({filters})} />
          <NotificationsButton/>
        </>}
      </div>
      <MapDataPointsMap onNoteSelected={(note) => history.push(`/Notes/${note.id}/`)}
                        filters={filters} selectLocation={selectLocation} location={location} />
      {note &&
        <MapDataPointModal note={note}
                           onClose={() => {refreshNote(note); history.push('/Notes/')}}
                           showOnMap={() => {this.setState({location: note}); history.push('/Notes/')}}
                           requestLocation={this.requestLocation}
                           cancelLocationRequest={this.cancelLocationRequest} />
      }
    </div>;
  }

  requestLocation = (onLocationSelected: (l: Location) => any, initial?: Location) => {
    const selectLocation = (l: Location) => {
      onLocationSelected(l);
      this.setState({selectLocation: undefined})
    };
    this.setState(initial ? {selectLocation, location: initial} : {selectLocation});
  };

  cancelLocationRequest = () => {
      this.setState({selectLocation: undefined});
  }
}

export default withRouter(MapDataPointsEditor)