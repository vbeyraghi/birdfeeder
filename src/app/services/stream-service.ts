import {Injectable, signal} from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class StreamService {
  private active = signal(false);
  public readonly isActive = this.active.asReadonly();

  start() {
    this.active.set(true);
  }

  stop() {
    this.active.set(false);
  }
}
