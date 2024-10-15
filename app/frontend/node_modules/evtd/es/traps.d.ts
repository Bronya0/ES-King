export interface TrapEventMap {
    mousemoveoutside: MouseEvent;
    clickoutside: MouseEvent;
}
declare type TrapEventNames = keyof TrapEventMap;
declare function trapOn(name: TrapEventNames, el: Element, handler: (e: Event) => any, options?: boolean | EventListenerOptions): boolean;
declare function trapOff(name: TrapEventNames, el: Element, handler: (e: Event) => any, options?: boolean | EventListenerOptions): boolean;
export { trapOff, trapOn };
