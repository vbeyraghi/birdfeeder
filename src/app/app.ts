import {Component, inject, signal} from '@angular/core';
import {VideoStream} from "./components/video-stream/video-stream";
import {toSignal} from "@angular/core/rxjs-interop";
import {ConfigService} from "./services/config-service";

@Component({
    selector: 'app-root',
    imports: [VideoStream],
    templateUrl: './app.html',
    styleUrl: './app.scss'
})
export class App {

    protected showPlayButton = signal(true);
    private readonly configService = inject(ConfigService);
    protected readonly title = toSignal(this.configService.getTitle$())
    protected readonly welcomeMessage = toSignal(this.configService.getDescription$())
    protected readonly startStreamMessage = toSignal(this.configService.getStartStreamMessage$())

    startStream() {
        this.showPlayButton.set(false);
    }


}
