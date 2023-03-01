import React from 'react';
import sessionRequest from "sessionRequest";
import {mapDataPointsUrl, mapDataPointUrl} from "urls";
import {AppContext, MapDataPointsContextType, MapDataPoint, MapDataPointsContext} from "components/types";

type MapDataPointsContextProps = {}

type MapDataPointsContextState = {
  mapDataPoints?: MapDataPoint[],
  error?: boolean,
}

const initialState: MapDataPointsContextState = {};

export default class MapDataPointsContextProvider extends React.Component<MapDataPointsContextProps, MapDataPointsContextState> {
  state = initialState;
  static contextType = AppContext;

  render() {
    const {children} = this.props;
    const {user} = this.context;

    const context: MapDataPointsContextType = {
      ...this.state, user, addNote: this.addNote, refreshNote: this.refreshNote, loadMapDataPoints: this.loadMapDataPoints};
    return <MapDataPointsContext.Provider value={context}>
      {children}
    </MapDataPointsContext.Provider>;
  }

  componentDidMount() {
    this.loadMapDataPoints();
  }

  loadMapDataPoints = () => {
    sessionRequest(mapDataPointsUrl + '?page_size=1000').then((response: any) => {
      if (response.status < 300)
        response.json().then((response: any) => {
          this.setState({mapDataPoints: response.results});
        });
    })
  };

  refreshNote = (note: MapDataPoint) => {
    return sessionRequest(mapDataPointUrl(note.id as number))
      .then(response => {
        if (!this.state.mapDataPoints) return;
        const mapDataPoints = this.state.mapDataPoints.slice();
        const index = mapDataPoints.findIndex(note2 => note2.id == note.id);

        if (response.status == 404) { // The note has been rejected
          mapDataPoints.splice(index, 1);
          this.setState({mapDataPoints});
        }

        else if (response.status == 200)
          response.json().then(note => {
            // Align created_by with how it is serialized in the note list response:
            if (note.created_by && typeof note.created_by !== "number") note.created_by = note.created_by.id;
            mapDataPoints.splice(index, 1, note);
            this.setState({mapDataPoints});
          });
      })
  };

  addNote = (note: MapDataPoint) => {
    if (!this.state.mapDataPoints) return;
    // Align created_by with how it is serialized in the note list response:
    if (note.created_by && typeof note.created_by !== "number") note.created_by = note.created_by.id;
    const mapDataPoints = this.state.mapDataPoints.slice();
    mapDataPoints.push(note);
    this.setState({mapDataPoints});
  };
}
