import {Component, inject, OnInit, signal} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {ConfigService} from '../../services/config-service';
import {StreamService} from '../../services/stream-service';
import {switchMap, take} from 'rxjs';

interface GalleryMedia {
  filename: string;
  url: string;
  timestamp: string;
  type: 'image' | 'video';
}

@Component({
  selector: 'gallery',
  templateUrl: './gallery.html',
  styleUrl: './gallery.scss',
  standalone: true,
  imports: []
})
export class Gallery implements OnInit {
  // Signal for collapsed state
  protected isCollapsed = signal(false);
  protected media = signal<GalleryMedia[]>([]);
  protected isCapturing = signal(false);
  protected isClipping = signal(false);
  protected isDeleting = signal(false);
  protected selectedMedia = signal<GalleryMedia | null>(null);
  private readonly http = inject(HttpClient);
  private readonly configService = inject(ConfigService);
  private readonly streamService = inject(StreamService);
  protected readonly isStreamActive = this.streamService.isActive;

  ngOnInit() {
    this.loadGallery();
  }

  loadGallery() {
    this.configService.getGalleryUrl$().pipe(
      take(1),
      switchMap(url => this.http.get<string[]>(url)),
      switchMap(async (filenames) => {
        const baseUrl = await this.configService.getGalleryUrl$().toPromise();
        return filenames.map(filename => ({
          filename,
          url: `${baseUrl}/${filename}`,
          timestamp: this.parseTimestamp(filename),
          type: filename.endsWith('.mp4') ? 'video' : 'image'
        } as GalleryMedia)); // We don't reverse here because backend already returns newest first
      })
    ).subscribe({
      next: (media) => this.media.set(media),
      error: (err) => console.error('Failed to load gallery', err)
    });
  }

  captureImage() {
    if (this.isCapturing()) return;

    this.isCapturing.set(true);
    this.configService.getCaptureUrl$().pipe(
      take(1),
      switchMap(url => this.http.post(url, {}))
    ).subscribe({
      next: () => {
        this.isCapturing.set(false);
        this.loadGallery();
      },
      error: (err) => {
        console.error('Capture failed', err);
        this.isCapturing.set(false);
      }
    });
  }

  captureClip() {
    if (this.isClipping()) return;

    this.isClipping.set(true);
    this.configService.getClipUrl$().pipe(
      take(1),
      switchMap(url => this.http.post(url, {}))
    ).subscribe({
      next: () => {
        this.isClipping.set(false);
        this.loadGallery();
      },
      error: (err) => {
        console.error('Clip capture failed', err);
        this.isClipping.set(false);
      }
    });
  }

  selectMedia(media: GalleryMedia | null) {
    this.selectedMedia.set(media);
  }

  deleteMedia(media: GalleryMedia) {
    if (this.isDeleting()) return;

    if (!confirm(`Are you sure you want to delete ${media.filename}?`)) return;

    this.isDeleting.set(true);
    this.configService.getDeleteMediaUrl$().pipe(
      take(1),
      switchMap(url => this.http.delete(`${url}/${media.filename}`))
    ).subscribe({
      next: () => {
        this.isDeleting.set(false);
        this.selectedMedia.set(null);
        this.loadGallery();
      },
      error: (err) => {
        console.error('Delete failed', err);
        this.isDeleting.set(false);
        alert('Failed to delete media.');
      }
    });
  }

  toggleCollapse() {
    this.isCollapsed.set(!this.isCollapsed());
  }

  private parseTimestamp(filename: string): string {
    // Expected format: capture_20240320_143005.jpg or clip_20240320_143005.mp4
    const parts = filename.split('_');
    if (parts.length < 3) return 'Unknown';
    
    const dateStr = parts[1]; // 20240320
    const timeStr = parts[2].split('.')[0]; // 143005

    const year = dateStr.substring(0, 4);
    const month = dateStr.substring(4, 6);
    const day = dateStr.substring(6, 8);
    const hour = timeStr.substring(0, 2);
    const min = timeStr.substring(2, 4);

    return `${year}-${month}-${day} ${hour}:${min}`;
  }
}
