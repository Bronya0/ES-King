import { on, off } from './delegate';
import { getEventTarget } from './utils';
const traps = {
    mousemoveoutside: new WeakMap(),
    clickoutside: new WeakMap()
};
function createTrapHandler(name, el, originalHandler) {
    if (name === 'mousemoveoutside') {
        const moveHandler = (e) => {
            if (el.contains(getEventTarget(e)))
                return;
            originalHandler(e);
        };
        return {
            mousemove: moveHandler,
            touchstart: moveHandler
        };
    }
    else if (name === 'clickoutside') {
        let mouseDownOutside = false;
        const downHandler = (e) => {
            mouseDownOutside = !el.contains(getEventTarget(e));
        };
        const upHanlder = (e) => {
            if (!mouseDownOutside)
                return;
            if (el.contains(getEventTarget(e)))
                return;
            originalHandler(e);
        };
        return {
            mousedown: downHandler,
            mouseup: upHanlder,
            touchstart: downHandler,
            touchend: upHanlder
        };
    }
    console.error(
    // eslint-disable-next-line @typescript-eslint/restrict-template-expressions
    `[evtd/create-trap-handler]: name \`${name}\` is invalid. This could be a bug of evtd.`);
    return {};
}
function ensureTrapHandlers(name, el, handler) {
    const handlers = traps[name];
    let elHandlers = handlers.get(el);
    if (elHandlers === undefined) {
        handlers.set(el, (elHandlers = new WeakMap()));
    }
    let trapHandler = elHandlers.get(handler);
    if (trapHandler === undefined) {
        elHandlers.set(handler, (trapHandler = createTrapHandler(name, el, handler)));
    }
    return trapHandler;
}
function trapOn(name, el, handler, options) {
    if (name === 'mousemoveoutside' || name === 'clickoutside') {
        const trapHandlers = ensureTrapHandlers(name, el, handler);
        Object.keys(trapHandlers).forEach((key) => {
            on(key, document, trapHandlers[key], options);
        });
        return true;
    }
    return false;
}
function trapOff(name, el, handler, options) {
    if (name === 'mousemoveoutside' || name === 'clickoutside') {
        const trapHandlers = ensureTrapHandlers(name, el, handler);
        Object.keys(trapHandlers).forEach((key) => {
            off(key, document, trapHandlers[key], options);
        });
        return true;
    }
    return false;
}
export { trapOff, trapOn };
