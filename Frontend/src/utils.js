/* eslint-disable no-param-reassign */

export function dateFormatterStart(datestring) {
  // converts an API datestring into the standard format Mon 30/01/1990, 10:21
  if (!datestring) return '';
  const date = new Date(datestring);
  return date.toLocaleString('en-GB', {
    weekday: 'short',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function dateFormatterEnd(datestring) {
  // converts an API datestring into the standard format 10:21
  if (!datestring) return '';
  const date = new Date(datestring);
  return date.toLocaleString('en-GB', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function dateFormatter(timeslot) {
  const start = dateFormatterStart(timeslot.start);
  const end = dateFormatterEnd(timeslot.end);
  return `${start} - ${end}`;
}


export function isOverlappingTime(dateTime1, dateTime2) {
  // checks if there is a overlap between to timeslots
  return (!(Date.parse(dateTime1.start) >= Date.parse(dateTime2.end)
            || Date.parse(dateTime2.start) >= Date.parse(dateTime1.end)));
}
