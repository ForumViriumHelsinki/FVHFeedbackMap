import React from "react";

export type User = {
    id: number,
    is_reviewer: boolean,
    username: string,
    first_name: string,
    last_name: string,
    phone_number: string
};

type userId = number

export type MapDataPointComment = {
    created_at: string,
    comment: string,
    user: string,
    id: number,
    map_data_point: number
}

export type MapDataPoint = {
    id?: number,
    image?: any,
    lat?: number,
    lon?: number,
    comment?: string,
    is_processed?: boolean,
    tags?: string[],
    modified_at?: string,
    created_at?: string,
    created_by?: number | {
        id: number,
        username: string
    },
    upvotes?: userId[],
    downvotes?: userId[],
    comments?: MapDataPointComment[],
};

export type Notification = {
    id: number,
    comment: MapDataPointComment
}

export type JSONSchema = any

export type AppContextType = {
  user?: User
}

export const AppContext = React.createContext({} as AppContextType);

export type MapDataPointsContextType = {
  mapDataPoints?: MapDataPoint[],
  addNote: (note: MapDataPoint) => any,
  refreshNote: (note: MapDataPoint) => any,
  loadMapDataPoints: () => any,
  user?: User
}

export const MapDataPointsContext = React.createContext({} as MapDataPointsContextType);

export type TagColor = 'primary' | 'secondary' | 'green' | 'red';

export type Tag = {
  tag: string,
  color: TagColor,
  icon: string,
}