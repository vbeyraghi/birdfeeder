import {AfterViewInit, Component, ElementRef, ViewChild} from '@angular/core';
import Hls from "hls.js";

@Component({
    selector: 'video-stream',
    templateUrl: './video-stream.html',
    styleUrl: './video-stream.scss',
    imports: []
})
export class VideoStream implements AfterViewInit {

    @ViewChild('videoPlayer') videoPlayer!: ElementRef<HTMLVideoElement>;

    private requestFullscreen(): void {
        const video = this.videoPlayer.nativeElement;
        if (video.requestFullscreen) {
            video.requestFullscreen().catch(err => console.warn('Fullscreen request failed:', err));
        }
    }

    ngAfterViewInit() {
        const video = this.videoPlayer.nativeElement;
        const videoSrc = 'http://192.168.0.237:8080/stream.m3u8';

        if (video.canPlayType('application/vnd.apple.mpegurl')) {
            video.src = videoSrc;
            video.addEventListener('loadedmetadata', () => {
                video.play().catch(err => console.warn('Autoplay failed:', err));
            });
        } else if (Hls.isSupported()) {
            const hls = new Hls();
            hls.attachMedia(video);
            hls.on(Hls.Events.MEDIA_ATTACHED, () => {
                try {
                    hls.loadSource(videoSrc);
                    hls.on(Hls.Events.MANIFEST_PARSED, () => {
                        video.play().catch(err => console.warn('Autoplay failed:', err));
                    });
                    this.requestFullscreen();
                } catch (err) {
                    console.error('Error loading source:', err);
                }
            });
        }
    }

}
