"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getEventTarget = void 0;
function getEventTarget(e) {
    const path = e.composedPath();
    return path[0];
}
exports.getEventTarget = getEventTarget;
