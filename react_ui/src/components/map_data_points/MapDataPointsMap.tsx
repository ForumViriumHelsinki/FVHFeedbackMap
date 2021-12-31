import React from 'react';
import _ from 'lodash';
import * as L from 'leaflet';

import MyPositionMap from 'util_components/MyPositionMap';
import Map from "util_components/Map";
import {Location} from "util_components/types";

import {MapDataPointsContext, MapDataPoint} from "components/types";
import {LatLngLiteral} from "leaflet";
import {filterNotes} from "components/map_data_points/utils";

const markerColors = {
  new: '#ff5000',
  processed: '#28a745',
};

type MapDataPointsMapProps = {
  onNoteSelected?: (note: MapDataPoint) => any,
  selectLocation?: (l: Location) => any,
  filters?: any,
  location?: Location,
  zoom?: number,
  selectedNotes?: number[],
  mapDataPoints?: MapDataPoint[],
  useUrl?: boolean
}

type MapDataPointsMapState = {
}

const initialState: () => MapDataPointsMapState = () => ({});

export default class MapDataPointsMap extends React.Component<MapDataPointsMapProps, MapDataPointsMapState> {
  state: MapDataPointsMapState = initialState();

  static contextType = MapDataPointsContext;

  private mapLayer?: any;
  private dotMarkers: {[id: string]: any} = {};

  render() {
    const {selectLocation, location, zoom, useUrl} = this.props;

    return <>
      <MyPositionMap onLocationSelected={selectLocation} location={location} zoom={zoom} useUrl={useUrl !== false}
                     extraLayers={_.filter([this.getMapLayer()])}/>
    </>;
  }

  getMapLayer() {
    const {filters, onNoteSelected, selectedNotes} = this.props;
    const mapDataPoints = this.props.mapDataPoints || this.context.mapDataPoints;

    if (!this.mapLayer) this.mapLayer = L.layerGroup();
    if (!mapDataPoints) return this.mapLayer;
    const filteredMapDataPoints = filterNotes(filters, mapDataPoints);

    filteredMapDataPoints.forEach((mapDataPoint: MapDataPoint) => {
      const id = String(mapDataPoint.id);
      const category = mapDataPoint.is_processed ? 'processed' : 'new';
      const style = {
        radius: 2,
        color: markerColors[category],
        opacity: selectedNotes && selectedNotes.includes(mapDataPoint.id as number) ? 0.4 : 0.05,
        weight: 20,
        fillColor: markerColors[category],
        fillOpacity: 1
      };
      const latLng = {lng: mapDataPoint.lon, lat: mapDataPoint.lat} as LatLngLiteral;
      if (this.dotMarkers[id]) return this.dotMarkers[id].setStyle(style).setLatLng(latLng);

      const marker = L.circleMarker(latLng, style);
      if (onNoteSelected) marker.on('click', () => onNoteSelected(mapDataPoint));
      marker.addTo(this.mapLayer);
      this.dotMarkers[id] = marker;
    });

    const index = _.keyBy(filteredMapDataPoints, 'id');
    Object.entries(this.dotMarkers).filter(([id]) => !index[id]).forEach(([id, marker]) => {
      marker.remove();
      delete this.dotMarkers[id];
    });
    return this.mapLayer;
  }
}

export class SimpleMapDataPointsMap extends MapDataPointsMap {
  render() {
    const {selectLocation, location, zoom} = this.props;
    if (!location) return <></>;

    return <Map latLng={[location.lat, location.lon]} extraLayers={[this.getMapLayer()]} zoom={zoom} />;
  }
}
