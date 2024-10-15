# evtd
Event delegation with native events and extended events in a small library.

(Only 300 lines of codes)
## Docs
[evtd](https://evtd.vercel.app/)

## Basic Usage
```ts
import { on, off } from 'evtd'

function handleClick () {
  console.log('click')
}

// register event
on(window, 'click', handleClick)
on(document, 'click', handleClick)
on(eventTarget, 'click', handleClick)

// evtd has 2 extended events
on(eventTarget, 'clickoutside', handleClick)
on(eventTarget, 'mousemoveoutside', handleClick)

// unregister
const handleClick2 = () => console.log('click2')
on(eventTarget, 'click', handleClick2)
off(eventTarget, 'click', handleClick2)

// capture
on(eventTarget, 'click', handleClick2, true)
off(eventTarget, 'click', handleClick2, true)
```

## License
MIT

Inspired by [delegated-events](https://github.com/dgraham/delegated-events)