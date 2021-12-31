import {LocationTuple} from "util_components/types";

export const loginUrl = '/rest-auth/login/';
export const registerUrl = '/rest-auth/registration/';
export const passwordResetUrl = '/rest-auth/password/reset/';
export const changePasswordUrl = '/rest-auth/password/reset/confirm/';

export const mapDataPointsUrl = "/rest/map_data_points/";
export const mapDataPointUrl = (id: number) => `/rest/map_data_points/${id}/`;

export const processedMapDataPointUrl = (id: number) => `/rest/map_data_points/${id}/mark_processed/`;
export const rejectMapDataPointUrl = (id: number) => `/rest/map_data_points/${id}/hide_note/`;

export const upvoteMapDataPointUrl = (id: number) => `/rest/map_data_points/${id}/upvote/`;
export const downvoteMapDataPointUrl = (id: number) => `/rest/map_data_points/${id}/downvote/`;

export const mapDataPointCommentsUrl = `/rest/map_data_point_comments/`;
export const mapDataPointCommentUrl = (id: number) => `/rest/map_data_point_comments/${id}/`;

export const notificationsUrl = `/rest/notifications/`;
export const notificationSeenUrl = (id: number) => `/rest/notifications/${id}/mark_seen/`;
export const recentMappersUrl = '/rest/recent_mappers/';

export const tagsUrl = '/rest/tags/';
