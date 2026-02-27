import {AfterViewInit, Component, ElementRef, inject, OnDestroy, ViewChild} from '@angular/core';
import Hls from "hls.js";
import {ConfigService} from "../../services/config-service";
import {Subscription} from "rxjs";

@Component({
    selector: 'video-stream',
    templateUrl: './video-stream.html',
    styleUrl: './video-stream.scss',
    imports: []
})
export class VideoStream implements AfterViewInit, OnDestroy {

    @ViewChild('videoPlayer') videoPlayer!: ElementRef<HTMLVideoElement>;
    private readonly configService: ConfigService = inject(ConfigService);
    private readonly subscription = new Subscription();

    ngAfterViewInit(): void {
        const videoElement = this.videoPlayer.nativeElement;

        this.subscription.add(this.configService.getStreamUrl$().subscribe((streamUrl) => {
            this.initHlsPlayback(videoElement, streamUrl);
        }));
    }

    ngOnDestroy(): void {
        this.subscription.unsubscribe();
    }

    private initHlsPlayback(videoElement: HTMLVideoElement, streamUrl: string): void {
        if (!Hls.isSupported()) {
            console.warn('HLS is not supported in this browser.');
            return;
        }

        const hls = this.createHls();
        hls.attachMedia(videoElement);

        hls.on(Hls.Events.MEDIA_ATTACHED, () => {
            try {
                hls.loadSource(streamUrl);

                hls.on(Hls.Events.MANIFEST_PARSED, () => {
                    videoElement.play().catch(err => console.warn('Autoplay failed:', err));
                });
            } catch (err) {
                console.error('Error loading source:', err);
            }
        });
    }

    private createHls(): Hls {
        const withCredentials: (xhr: XMLHttpRequest) => void = (xhr) => {
            xhr.withCredentials = true;
        };

        return new Hls({xhrSetup: withCredentials});
    }
}