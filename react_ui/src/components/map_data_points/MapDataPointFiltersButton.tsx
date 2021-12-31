import React from 'react';
// @ts-ignore
import _ from 'lodash';
// @ts-ignore
import {ButtonDropdown, DropdownItem, DropdownMenu, DropdownToggle} from "reactstrap";
import {AppContext, MapDataPoint, Tag, User} from "components/types";
import MapToolButton from "components/map_data_points/MapToolButton";
import sessionRequest from "sessionRequest";
import {recentMappersUrl} from "urls";
import {filterNotes, getTags} from "components/map_data_points/utils";


type MapDataPointFiltersButtonProps = {
  onFiltersChanged: (filters: any) => any,
  mapDataPoints?: MapDataPoint[]
}

type MapDataPointFiltersButtonState = {
  filters: any,
  counts: any,
  filtersOpen: boolean,
  recentMappers?: User[],
  mappersOpen?: boolean,
  tags?: Tag[]
}

const initialState: () => MapDataPointFiltersButtonState = () => ({
  filters: {},
  counts: {},
  filtersOpen: false
});

const _24h = 24 * 3600 * 1000;
const _90d = 90 * _24h;

const filter24h = (note: MapDataPoint) =>
  // @ts-ignore
  new Date(note.modified_at || note.created_at).valueOf() > new Date().valueOf() - _24h;

const filter90d = (note: MapDataPoint) =>
  // @ts-ignore
  new Date(note.modified_at || note.created_at).valueOf() > new Date().valueOf() - _90d;

export default class MapDataPointFiltersButton extends React.Component<MapDataPointFiltersButtonProps, MapDataPointFiltersButtonState> {
  state: MapDataPointFiltersButtonState = initialState();
  static contextType = AppContext;

  componentDidMount() {
    sessionRequest(recentMappersUrl).then(response => response.json())
      .then((recentMappers) => this.setState({recentMappers}))
    getTags.then((tags) => this.setState({tags}));
  }

  componentDidUpdate(prevProps: Readonly<MapDataPointFiltersButtonProps>) {
    const notes = this.props.mapDataPoints;
    if (notes && (prevProps.mapDataPoints != notes)) {
      const filters = Object.entries(this.filterOptions());
      const counts = filters.map(([k, v]) => [k, filterNotes(v, notes).length]);
      this.setState({counts: Object.fromEntries(counts)})
    }
  }

  filterOptions() {
    const {user} = this.context;
    const {recentMappers, tags} = this.state;

    return {
      '24h': {newer_than: filter24h},
      '90 days': {newer_than: filter90d},
      'My notes': {created_by: user && user.id},

      'New': {is_processed: false},
      'Processed': {is_processed: true},

      ...Object.fromEntries((recentMappers || []).map((mapper) => [mapper.username, {created_by: mapper.id}])),
      ...Object.fromEntries((tags || []).map(({tag}) => [tag, {tags: [tag]}])),
    }
  }

  render() {
    const {filters, filtersOpen, recentMappers, mappersOpen, counts, tags} = this.state;
    const filterOptions = this.filterOptions();

    const FilterItem = ({label}: {label: string}) => {
      // @ts-ignore
      const filter = filterOptions[label];
      const active = _.isMatch(filters, filter) || (filter.tags && (filters.tags || []).includes(filter.tags[0]));
      return <DropdownItem className={active ? 'text-primary pr-1' : 'pr-1'}
                                                                onClick={() => this.toggleFilter(filter)}>
        <span className="float-right small position-relative">{counts[label] || ''}</span>
        <span className="mr-4">{label}</span>
      </DropdownItem>
    };

    return <ButtonDropdown isOpen={filtersOpen} toggle={() => this.setState({filtersOpen: !filtersOpen})}>
      <DropdownToggle tag="span">
        <MapToolButton icon="filter_alt"/>
      </DropdownToggle>
      <DropdownMenu>
        <DropdownItem header>Filter</DropdownItem>
        <FilterItem label={'24h'}/>
        <FilterItem label={'90 days'}/>
        <FilterItem label={'My notes'}/>
        {recentMappers &&
          <div className="dropleft btn-group">
            <button className="dropdown-item" onClick={() => this.setState({mappersOpen: !mappersOpen})}>
              By mapper...
            </button>
            {mappersOpen && <DropdownMenu>
              {recentMappers.map(mapper => <FilterItem label={mapper.username} key={mapper.id}/>)}
            </DropdownMenu>}
          </div>
        }
        <DropdownItem divider/>
        <FilterItem label={'New'}/>
        <FilterItem label={'Processed'}/>
        {tags && <>
          <DropdownItem divider/>
          {tags.map(({tag}) => <FilterItem label={tag} key={tag}/>)}
        </>}
      </DropdownMenu>
    </ButtonDropdown>
  }

  private toggleFilter(filter: any) {
    const filters = Object.assign({}, this.state.filters);

    if (filter.tags) {
      const tag = filter.tags[0];
      if (filters.tags && filters.tags.includes(tag)) {
        filters.tags = _.without(filters.tags, tag);
        if (!filters.tags.length) delete filters.tags;
      }
      else filters.tags = filter.tags;
    }
    else if (_.isMatch(filters, filter)) Object.keys(filter).forEach(k => delete filters[k]);
    else Object.assign(filters, filter);
    this.setFilters(filters);
  }

  setFilters(filters: any) {
    this.setState({filters});
    this.props.onFiltersChanged(filters);
  }
}
