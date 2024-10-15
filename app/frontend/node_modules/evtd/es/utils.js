export function getEventTarget(e) {
    const path = e.composedPath();
    return path[0];
}
