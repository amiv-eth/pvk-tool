import m from 'mithril';
import { Card, Button } from 'polythene-mithril';
import { addTypography, addLayoutStyles } from 'polythene-css';

addTypography();
addLayoutStyles(); // to use m('.flex')

export default class SidebarCard {
  static view({
    attrs: {
      title,
      subtitle = '',
      content,
      actionName = undefined,
      actionActive = true,
      action = undefined,
    },
  }) {
    return m(Card, {
      content: [
        {
          header: { title, subtitle },
        },
        {
          text: { content },
        },
      ].concat((actionName && action) ? [{
        actions: {
          content: [
            m('.flex'),
            m(Button, {
              label: actionName,
              inactive: !actionActive || !action,
              events: { onclick: action },
            }),
          ],
        },
      }] : []),
    });
  }
}
