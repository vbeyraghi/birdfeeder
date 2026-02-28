import {Component, inject, signal} from '@angular/core';
import {VideoStream} from "./components/video-stream/video-stream";
import {SolarMonitor} from "./components/solar-monitor/solar-monitor";
import {Gallery} from "./components/gallery/gallery";
import {toSignal} from "@angular/core/rxjs-interop";
import {ConfigService} from "./services/config-service";
import {StreamService} from "./services/stream-service";

@Component({
    selector: 'app-root',
    imports: [VideoStream, SolarMonitor, Gallery],
    templateUrl: './app.html',
    styleUrl: './app.scss'
})
export class App {

    protected showPlayButton = signal(true);
    private readonly configService = inject(ConfigService);
    protected readonly title = toSignal(this.configService.getTitle$())
    protected readonly welcomeMessage = toSignal(this.configService.getDescription$())
    protected readonly startStreamMessage = toSignal(this.configService.getStartStreamMessage$())
    private readonly streamService = inject(StreamService);

    startStream() {
        this.showPlayButton.set(false);
        this.streamService.start();
    }


}
