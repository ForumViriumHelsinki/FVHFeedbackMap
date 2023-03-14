import React from 'react';
// @ts-ignore
import {HashRouter as Router, Route, Switch, useParams, Redirect} from "react-router-dom";

import sessionRequest, {logout} from "sessionRequest";

import LoginScreen from 'components/LoginScreen';
import LoadScreen from "components/LoadScreen";
import {AppContext, User} from "components/types";
import ResetPasswordScreen from "components/ResetPasswordScreen";
import MapDataPointModal from "components/map_data_points/MapDataPointModal";
import NavBar from "util_components/bootstrap/NavBar";
import Confirm from "util_components/bootstrap/Confirm";
import MapDataPointsEditor from "components/map_data_points/MapDataPointsEditor";
import MapDataPointsContextProvider from "components/map_data_points/MapDataPointsContextProvider";
import TagButtons from "components/TagButtons";

type UIState = {
  user?: User,
  dataFetched: boolean,
  showLogout: boolean,
  menuOpen: boolean
}

class MainUI extends React.Component<{}, UIState> {
  state: UIState = {
    user: undefined,
    dataFetched: false,
    showLogout: false,
    menuOpen: false
  };

  componentDidMount() {
    this.refreshUser();
    window.addEventListener('resize', this.onResize)
  }

  refreshUser() {
    sessionRequest('/rest-auth/user/').then(response => {
      if (response.status == 401) this.setState({user: undefined, dataFetched: true});
      else response.json().then(user => this.setState({user, dataFetched: true}));
    })
  }

  logout = () => {
    sessionRequest('/rest-auth/logout/', {method: 'POST'}).then(response => {
      logout();
      this.setState({user: undefined});
    });
  };

  onResize = () => {
    const el = document.getElementById('MainUI');
    // @ts-ignore
    if (el) el.style.height = window.innerHeight;
  };

  componentWillUnmount() {
    window.removeEventListener('resize', this.onResize)
  }

  render() {
    const {user, dataFetched, showLogout} = this.state;

    // @ts-ignore
    const MapDataPoint = () => <MapDataPointModal note={{id: useParams().noteId}} fullScreen />;

    const ResetPassword = () => {
      const params = useParams() as any;
      return <ResetPasswordScreen uid={params.uid} token={params.token}/>;
    };

    const MainUI = (props: {selectedNoteId?: number, newNote?: boolean, osmFeatures?: number[], buttons?: boolean}) =>
      <div style={{height: window.innerHeight}} className="flex-column d-flex" id="MainUI">
        {!props.buttons &&
          <NavBar onIconClick={this.onNavIconClick}
                  icon={user ? "account_circle" : "login"}
                  iconText={user ? user.username : 'Kirjaudu'}>
            <h4 className="m-2">FVH Palautekartta</h4>
          </NavBar>
        }
        <div className="flex-grow-1 flex-shrink-1 overflow-auto">
          {props.buttons ? <TagButtons/> :
            <MapDataPointsContextProvider>
              <MapDataPointsEditor {...props}/>
            </MapDataPointsContextProvider>}
        </div>
      </div>;

    return dataFetched ? <AppContext.Provider value={{user}}>
      <Router>
        <Switch>
          <Route path='/login/'>
            {user ? <Redirect to="" /> : <LoginScreen onLogin={() => this.refreshUser()}/>}
          </Route>
          <Route path='/resetPassword/:uid/:token'>
            <ResetPassword/>
          </Route>
          <Route path='/note/:noteId'>
            <MapDataPoint/>
          </Route>
          <Route path='/Notes/new/:osmId(\d+)?/' render={(props: any) => {
            const {osmId} = props.match.params;
            return <MainUI newNote osmFeatures={osmId && [Number(osmId)]}/>
          }} />
          <Route path='/Notes/:noteId(\d+)?' render={(props: any) =>
            <MainUI selectedNoteId={props.match.params.noteId && Number(props.match.params.noteId)}/>
          } />
          <Route path='/map/' render={(props: any) =>
            <MainUI />
          } />
          <Route path='/'><MainUI buttons/></Route>
        </Switch>
      </Router>
      {showLogout &&
        <Confirm title="Log out?"
                 onClose={() => this.setState({showLogout: false})}
                 onConfirm={this.logout}/>
      }
    </AppContext.Provider> : <LoadScreen/>;
  }

  onNavIconClick = () => {
    if (this.state.user) this.setState({showLogout: true});
    else window.location.hash = '#/login/'
  }
}

export default MainUI;
