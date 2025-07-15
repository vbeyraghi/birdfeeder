import {Component, signal} from '@angular/core';
import {VideoStream} from "./video-stream/video-stream";

@Component({
  selector: 'app-root',
  imports: [VideoStream],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('birdfeeder');
  protected showPlayButton = signal(true);

  startStream() {
    this.showPlayButton.set(false);
  }
}
