"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.off = exports.on = void 0;
const traps_1 = require("./traps");
const utils_1 = require("./utils");
// currently `once` and `passive` is not supported
function createDelegate() {
    if (typeof window === 'undefined') {
        return {
            on: () => { },
            off: () => { }
        };
    }
    const propagationStopped = new WeakMap();
    const immediatePropagationStopped = new WeakMap();
    function trackPropagation() {
        propagationStopped.set(this, true);
    }
    function trackImmediate() {
        propagationStopped.set(this, true);
        immediatePropagationStopped.set(this, true);
    }
    function spy(event, propName, fn) {
        const source = event[propName];
        event[propName] = function () {
            fn.apply(event, arguments);
            return source.apply(event, arguments);
        };
        return event;
    }
    function unspy(event, propName) {
        event[propName] = Event.prototype[propName];
    }
    const currentTargets = new WeakMap();
    const currentTargetDescriptor = Object.getOwnPropertyDescriptor(Event.prototype, 'currentTarget');
    function getCurrentTarget() {
        var _a;
        return (_a = currentTargets.get(this)) !== null && _a !== void 0 ? _a : null;
    }
    function defineCurrentTarget(event, getter) {
        if (currentTargetDescriptor === undefined)
            return;
        Object.defineProperty(event, 'currentTarget', {
            configurable: true,
            enumerable: true,
            get: getter !== null && getter !== void 0 ? getter : currentTargetDescriptor.get
        });
    }
    const phaseToTypeToElToHandlers = {
        bubble: {},
        capture: {}
    };
    const typeToWindowEventHandlers = {};
    function createUnifiedHandler() {
        const delegeteHandler = function (e) {
            const { type, eventPhase, bubbles } = e;
            const target = (0, utils_1.getEventTarget)(e);
            if (eventPhase === 2)
                return;
            const phase = eventPhase === 1 ? 'capture' : 'bubble';
            let cursor = target;
            const path = [];
            // collecting bubble path
            while (true) {
                if (cursor === null)
                    cursor = window;
                path.push(cursor);
                if (cursor === window) {
                    break;
                }
                // eslint-disable-next-line @typescript-eslint/strict-boolean-expressions
                cursor = (cursor.parentNode || null);
            }
            const captureElToHandlers = phaseToTypeToElToHandlers.capture[type];
            const bubbleElToHandlers = phaseToTypeToElToHandlers.bubble[type];
            spy(e, 'stopPropagation', trackPropagation);
            spy(e, 'stopImmediatePropagation', trackImmediate);
            defineCurrentTarget(e, getCurrentTarget);
            if (phase === 'capture') {
                if (captureElToHandlers === undefined)
                    return;
                // capture
                for (let i = path.length - 1; i >= 0; --i) {
                    if (propagationStopped.has(e))
                        break;
                    const target = path[i];
                    const handlers = captureElToHandlers.get(target);
                    if (handlers !== undefined) {
                        currentTargets.set(e, target);
                        for (const handler of handlers) {
                            if (immediatePropagationStopped.has(e))
                                break;
                            handler(e);
                        }
                    }
                    if (i === 0 && !bubbles && bubbleElToHandlers !== undefined) {
                        const bubbleHandlers = bubbleElToHandlers.get(target);
                        if (bubbleHandlers !== undefined) {
                            for (const handler of bubbleHandlers) {
                                if (immediatePropagationStopped.has(e))
                                    break;
                                handler(e);
                            }
                        }
                    }
                }
            }
            else if (phase === 'bubble') {
                if (bubbleElToHandlers === undefined)
                    return;
                // bubble
                for (let i = 0; i < path.length; ++i) {
                    if (propagationStopped.has(e))
                        break;
                    const target = path[i];
                    const handlers = bubbleElToHandlers.get(target);
                    if (handlers !== undefined) {
                        currentTargets.set(e, target);
                        for (const handler of handlers) {
                            if (immediatePropagationStopped.has(e))
                                break;
                            handler(e);
                        }
                    }
                }
            }
            unspy(e, 'stopPropagation');
            unspy(e, 'stopImmediatePropagation');
            defineCurrentTarget(e);
        };
        delegeteHandler.displayName = 'evtdUnifiedHandler';
        return delegeteHandler;
    }
    function createUnifiedWindowEventHandler() {
        const delegateHandler = function (e) {
            const { type, eventPhase } = e;
            if (eventPhase !== 2)
                return;
            const handlers = typeToWindowEventHandlers[type];
            if (handlers === undefined)
                return;
            handlers.forEach((handler) => handler(e));
        };
        delegateHandler.displayName = 'evtdUnifiedWindowEventHandler';
        return delegateHandler;
    }
    const unifiedHandler = createUnifiedHandler();
    const unfiendWindowEventHandler = createUnifiedWindowEventHandler();
    function ensureElToHandlers(phase, type) {
        const phaseHandlers = phaseToTypeToElToHandlers[phase];
        if (phaseHandlers[type] === undefined) {
            phaseHandlers[type] = new Map();
            window.addEventListener(type, unifiedHandler, phase === 'capture');
        }
        return phaseHandlers[type];
    }
    function ensureWindowEventHandlers(type) {
        const windowEventHandlers = typeToWindowEventHandlers[type];
        if (windowEventHandlers === undefined) {
            typeToWindowEventHandlers[type] = new Set();
            window.addEventListener(type, unfiendWindowEventHandler);
        }
        return typeToWindowEventHandlers[type];
    }
    function ensureHandlers(elToHandlers, el) {
        let elHandlers = elToHandlers.get(el);
        if (elHandlers === undefined) {
            elToHandlers.set(el, (elHandlers = new Set()));
        }
        return elHandlers;
    }
    function handlerExist(el, phase, type, handler) {
        const elToHandlers = phaseToTypeToElToHandlers[phase][type];
        // phase ${type} event has handlers
        if (elToHandlers !== undefined) {
            const handlers = elToHandlers.get(el);
            // phase using el with ${type} event has handlers
            if (handlers !== undefined) {
                if (handlers.has(handler))
                    return true;
            }
        }
        return false;
    }
    function windowEventHandlerExist(type, handler) {
        const handlers = typeToWindowEventHandlers[type];
        if (handlers !== undefined) {
            if (handlers.has(handler)) {
                return true;
            }
        }
        return false;
    }
    function on(type, el, handler, options) {
        let mergedHandler;
        if (typeof options === 'object' && options.once === true) {
            mergedHandler = (e) => {
                off(type, el, mergedHandler, options);
                handler(e);
            };
        }
        else {
            mergedHandler = handler;
        }
        const trapped = (0, traps_1.trapOn)(type, el, mergedHandler, options);
        if (trapped)
            return;
        const phase = options === true ||
            (typeof options === 'object' && options.capture === true)
            ? 'capture'
            : 'bubble';
        const elToHandlers = ensureElToHandlers(phase, type);
        const handlers = ensureHandlers(elToHandlers, el);
        if (!handlers.has(mergedHandler))
            handlers.add(mergedHandler);
        if (el === window) {
            const windowEventHandlers = ensureWindowEventHandlers(type);
            if (!windowEventHandlers.has(mergedHandler)) {
                windowEventHandlers.add(mergedHandler);
            }
        }
    }
    function off(type, el, handler, options) {
        const trapped = (0, traps_1.trapOff)(type, el, handler, options);
        if (trapped)
            return;
        const capture = options === true ||
            (typeof options === 'object' && options.capture === true);
        const phase = capture ? 'capture' : 'bubble';
        const elToHandlers = ensureElToHandlers(phase, type);
        const handlers = ensureHandlers(elToHandlers, el);
        if (el === window) {
            const mirrorPhase = capture ? 'bubble' : 'capture';
            if (!handlerExist(el, mirrorPhase, type, handler) &&
                windowEventHandlerExist(type, handler)) {
                // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
                const windowEventHandlers = typeToWindowEventHandlers[type];
                windowEventHandlers.delete(handler);
                if (windowEventHandlers.size === 0) {
                    window.removeEventListener(type, unfiendWindowEventHandler);
                    typeToWindowEventHandlers[type] = undefined;
                }
            }
        }
        if (handlers.has(handler))
            handlers.delete(handler);
        if (handlers.size === 0) {
            elToHandlers.delete(el);
        }
        if (elToHandlers.size === 0) {
            window.removeEventListener(type, unifiedHandler, phase === 'capture');
            phaseToTypeToElToHandlers[phase][type] = undefined;
        }
    }
    return {
        on: on,
        off: off
    };
}
const { on, off } = createDelegate();
exports.on = on;
exports.off = off;
