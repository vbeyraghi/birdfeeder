import {AfterViewInit, Component, ElementRef, inject, ViewChild} from '@angular/core';
import Hls from "hls.js";
import {ConfigService} from "../../services/config-service";

@Component({
    selector: 'video-stream',
    templateUrl: './video-stream.html',
    styleUrl: './video-stream.scss',
    imports: []
})
export class VideoStream implements AfterViewInit {

    @ViewChild('videoPlayer') videoPlayer!: ElementRef<HTMLVideoElement>;
    private readonly configService: ConfigService = inject(ConfigService);

    ngAfterViewInit() {
        const video = this.videoPlayer.nativeElement;
        this.configService.getStreamUrl$().subscribe(
            videoSrc => {
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
        )
    }

    private requestFullscreen(): void {
        const video = this.videoPlayer.nativeElement;
        if (video.requestFullscreen) {
            video.requestFullscreen().catch(err => console.warn('Fullscreen request failed:', err));
        }
    }
}