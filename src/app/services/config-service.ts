import {inject, Injectable} from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {first, map, Observable, shareReplay} from "rxjs";
import {CONFIG_BATTERY_DATA_INTERVAL, CONFIG_BATTERY_DATA_URL, CONFIG_CAPTURE_URL, CONFIG_CLIP_URL, CONFIG_DELETE_MEDIA_URL, CONFIG_DESCRIPTION, CONFIG_GALLERY_URL, CONFIG_START_STREAM, CONFIG_STREAM_URL, CONFIG_TITLE} from "../constants/config-constants";

@Injectable({
    providedIn: 'root'
})
export class ConfigService {

    private readonly http: HttpClient = inject(HttpClient);
    private readonly config$: Observable<{ [key in string]: string }>

    constructor() {
        this.config$ = this.http.get<any>('/birdfeeder/assets/config.json').pipe(shareReplay(1));
    }

    getTitle$(): Observable<string> {
        return this.config$.pipe(map(config => config[CONFIG_TITLE]), first());
    }

    getDescription$(): Observable<string> {
        return this.config$.pipe(map(config => config[CONFIG_DESCRIPTION]), first());
    }

    getStreamUrl$(): Observable<string> {
        return this.config$.pipe(map(config => config[CONFIG_STREAM_URL]), first());
    }

    getStartStreamMessage$(): Observable<string> {
        return this.config$.pipe(map(config => config[CONFIG_START_STREAM]), first());
    }

    getBatteryDataUrl$(): Observable<string> {
        return this.config$.pipe(map(config => config[CONFIG_BATTERY_DATA_URL]), first());
    }

    getBatteryDataInterval$(): Observable<number> {
        return this.config$.pipe(
            map(config => {
                const val = config[CONFIG_BATTERY_DATA_INTERVAL];
                // Default to 5 minutes if not set or invalid
                const interval = parseInt(val, 10);
                return isNaN(interval) ? 5 : interval;
            }),
            first()
        );
    }

    getCaptureUrl$(): Observable<string> {
        return this.config$.pipe(map(config => config[CONFIG_CAPTURE_URL]), first());
    }

    getClipUrl$(): Observable<string> {
        return this.config$.pipe(map(config => config[CONFIG_CLIP_URL]), first());
    }

    getGalleryUrl$(): Observable<string> {
        return this.config$.pipe(map(config => config[CONFIG_GALLERY_URL]), first());
    }

    getDeleteMediaUrl$(): Observable<string> {
        return this.config$.pipe(map(config => config[CONFIG_DELETE_MEDIA_URL]), first());
    }
}
