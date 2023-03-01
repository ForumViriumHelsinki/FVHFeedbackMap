import {MapDataPoint, User} from "components/types";
import sessionRequest from "sessionRequest";
import {tagsUrl} from "urls";

export const userCanEditNote = (user: User | null, mapDataPoint: MapDataPoint) => {
  // @ts-ignore
  const is_creator = user && mapDataPoint.created_by && user.id == mapDataPoint.created_by.id;
  const newAnonymousNote = mapDataPoint.created_at && !user && !mapDataPoint.created_by &&
                           Date.parse(mapDataPoint.created_at) > Date.now() - 10 * 60 * 1000 || false;
  return (user && (user.is_reviewer || is_creator)) || !mapDataPoint.id || newAnonymousNote;
};

export const filterNotes = (filters: any, notes: MapDataPoint[]) => {
  if (!filters) return notes;
  const entries = Object.entries(filters || {});

  return notes.filter((note: MapDataPoint) => {
      for (const [key, value] of entries) {
        if (typeof value == 'function') {
          if (!value(note)) return false;
        }
        else if (value instanceof Array) for (const item of value) {
          // @ts-ignore
          if (!(note[key] || []).includes(item)) return false;
        }
        // @ts-ignore
        else if (note[key] != value) return false;
      }
      return true;
    });
};

export const getTags =
  sessionRequest(tagsUrl).then(r => r.json()).then(response => response.results);
