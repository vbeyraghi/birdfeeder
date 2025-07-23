import {inject, Injectable} from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {first, map, Observable, shareReplay} from "rxjs";
import {CONFIG_DESCRIPTION, CONFIG_START_STREAM, CONFIG_STREAM_URL, CONFIG_TITLE} from "../constants/config-constants";

@Injectable({
    providedIn: 'root'
})
export class ConfigService {

    private readonly http: HttpClient = inject(HttpClient);
    private readonly config$: Observable<{ [key in string]: string }>

    constructor() {
        this.config$ = this.http.get<any>('/assets/config.json').pipe(shareReplay(1));
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
}
