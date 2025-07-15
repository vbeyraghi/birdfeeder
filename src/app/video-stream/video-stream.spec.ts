import {ComponentFixture, TestBed} from '@angular/core/testing';

import {VideoStream} from './video-stream';

describe('VideoStream', () => {
  let component: VideoStream;
  let fixture: ComponentFixture<VideoStream>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VideoStream]
    })
    .compileComponents();

    fixture = TestBed.createComponent(VideoStream);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
