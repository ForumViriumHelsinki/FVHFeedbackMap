import React from 'react';

// @ts-ignore
import {Button, Spinner} from "reactstrap";
import Icon from "util_components/bootstrap/Icon";
import {LocationTuple, Location} from "util_components/types";
import Modal from "util_components/bootstrap/Modal";
import ErrorAlert from "util_components/bootstrap/ErrorAlert";

import sessionRequest from "sessionRequest";
import {mapDataPointsUrl, mapDataPointUrl} from "urls";
import {MapDataPointsContext, MapDataPoint} from "components/types";
import MapDataPointTags from "components/map_data_points/MapDataPointTags";
import Confirm from "util_components/bootstrap/Confirm";
import MapToolButton from "components/map_data_points/MapToolButton";


type NewMapDataPointProps = {
  requestNoteType?: boolean,
  osmFeatures?: number[]
  requestLocation: (cb: (l: Location) => any) => any,
  cancelLocationRequest: () => any
}

type NewMapDataPointState = MapDataPoint & {
  status: 'initial' | 'locating' | 'commenting' | 'thanks',
  submitting: boolean,
  error: boolean,
  imageError: boolean,
  imagesUploading: MapDataPoint[],
  tags: string[],
  mapFeatureSets: any,
  chooseNoteType?: boolean,
  confirmCancel?: boolean
}

const initialState: () => NewMapDataPointState = () => ({
  status: 'initial',
  lat: undefined,
  lon: undefined,
  image: undefined,
  comment: '',
  osm_features: [],
  addresses: [],
  error: false,
  imageError: false,
  submitting: false,
  imagesUploading: [],
  tags: [],
  mapFeatureSets: {},
  nearbyFeatures: [],
  nearbyAddresses: [],
});

const {imagesUploading, ...resetState} = initialState();

export default class NewMapDataPoint extends React.Component<NewMapDataPointProps, NewMapDataPointState> {
  state: NewMapDataPointState = initialState();
  static contextType = MapDataPointsContext;

  render() {
    const {mapFeatureTypes} = this.context;
    const {
      status, lat, lon, submitting, error, imageError, imagesUploading, tags,
      chooseNoteType, confirmCancel
    } = this.state;

    const location = [lon, lat] as LocationTuple;

    return <>
        <input name="image" id="image" className="d-none" type="file"
               accept="image/*" capture="environment"
               onChange={this.onImageCaptured}/>

        {imageError &&
          <Modal title="Image error" onClose={() => this.setState({imageError: false})}>
            There was an error uploading the image. Try again maybe?
          </Modal>
        }

        {{
          initial:
            <>
              {imagesUploading.length > 0 &&
                <Button outline disabled size="sm">
                  <Icon icon="cloud_upload"/> {imagesUploading.length} <Spinner size="sm"/>
                </Button>
              }
              <MapToolButton icon="camera_alt" onClick={this.onImageClick} />
              <MapToolButton icon="comment" onClick={this.onCommentClick} />
            </>,

          locating:
            <div className="mt-4 text-right">
              Scroll map to select position{' '}
              <MapToolButton onClick={this.onCancel}>
                Cancel
              </MapToolButton>
            </div>,
          commenting:
            <Modal title="Add comment" onClose={this.onCancel}>
              <ErrorAlert status={error} message="Submit failed. Try again maybe?"/>
              <textarea className="form-control" rows={5}
                        placeholder="Describe the problem / note (optional)"
                        onChange={(e) =>
                          this.setState({comment: e.target.value})} />
              <MapDataPointTags expanded tags={tags} onChange={tags => this.setState({tags})}/>
              <Button block disabled={submitting} color="primary" size="sm"
                      onClick={submitting ? undefined : this.onSubmit}>
                {submitting ? 'Submitting...' : 'Done'}
              </Button>
            </Modal>,
          thanks:
            <Modal title="Thank you" onClose={this.onCancel}>
              <p className="m-2">The comment was saved successfully.</p>
              {imagesUploading.length > 0 &&
                <p className="m-2">{imagesUploading.length} images are uploading in background.</p>
              }
              <Button block color="primary" size="sm" onClick={this.onCancel}>
                Close
              </Button>
            </Modal>,
        }[status]}

      {chooseNoteType &&
        <Modal onClose={() => this.setState({chooseNoteType: false})} title={<>
            <p>Add a new picture or textual note on the map:</p>
            <MapToolButton icon="camera_alt" onClick={this.onImageClick}>
               Open camera
            </MapToolButton>
            <MapToolButton icon="comment"
                           onClick={this.onCommentClick}>
              Add text
            </MapToolButton>
          </>}
        />
      }
      {confirmCancel &&
        <Confirm title="Close without saving?"
                 onConfirm={this.onConfirmCancel}
                 onClose={() => this.setState({confirmCancel: false})}/>
      }
    </>;
  }

  componentDidMount() {
    const {requestNoteType} = this.props;
    if (requestNoteType) this.setState({chooseNoteType: true});
  }

  onImageClick = () => {
    this.imageEl().click();
    this.setState({chooseNoteType: false});
  };

  onCommentClick = () => {
    this.props.requestLocation(this.onLocationSelected);
    this.setState({status: 'locating', chooseNoteType: false});
  };

  private imageEl() {
    return document.getElementById('image') as HTMLInputElement;
  }

  onImageCaptured = () => {
    const files = this.imageEl().files as FileList;
    this.props.requestLocation(this.onLocationSelected);
    this.setState({status: "locating", image: files[0]})
  };

  onLocationSelected = (location?: Location) => {
    if (location)
      this.setState({status: "commenting", ...location});
    else this.setState(resetState);
  };

  onCancel = () => {
    const status = this.state.status;
    if (status == 'commenting') this.setState({confirmCancel: true});
    else {
      if (status == 'locating') this.props.cancelLocationRequest();
      this.setState(resetState);
    }
  };

  onConfirmCancel = () => {
    this.setState(resetState);
  };

  onSubmit = () => {
    const {comment, lon, lat, image, imagesUploading, tags} = this.state;
    const fields = {comment, lat, lon, tags};
    const {addNote} = this.context;

    this.setState({submitting: true});

    sessionRequest(mapDataPointsUrl, {method: 'POST', data: fields})
    .then((response: any) => {
      if ((response.status >= 300)) return this.setState({error: true, submitting: false});
      response.json().then((data: MapDataPoint) => {
        this.setState({...resetState, status: "thanks"});

        if (!image) {
          addNote(data);
          return;
        }

        let formData = new FormData();
        formData.append('image', image);
        this.setState({imagesUploading: imagesUploading.concat([data])});
        sessionRequest(mapDataPointUrl(data.id as number), {method: 'PATCH', body: formData})
        .then((response: any) => {
          const uploading = this.state.imagesUploading.slice();
          uploading.splice(uploading.indexOf(data, 1));
          this.setState({imagesUploading: uploading});

          if ((response.status >= 300)) this.setState({imageError: true});
          addNote(data);
        });
      });
    });
  };
}
