import {computed, inject, Injectable, signal} from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {ConfigService} from "./config-service";
import {switchMap, timer} from "rxjs";

export interface BatteryData {
  timestamp: string;
  percentage: number;
  solar_radiation_Wm2: number;
}

@Injectable({
  providedIn: 'root'
})
export class SolarService {
  public readonly efficiency = computed(() => {
    const last = this.lastData();
    if (!last || last.solar_radiation_Wm2 === 0) return 0;
    // Arbitrary efficiency formula for "fun" display: (radiation / max_expected_radiation) * 100
    // Assuming 1000 W/m2 is peak sun
    return (last.solar_radiation_Wm2 / 1000) * 100;
  });
  public readonly isCharging = computed(() => {
    return this.calculateRate() > 0.01; // Require a minimal positive trend
  });
  public readonly estimatedUptime = computed(() => {
    const last = this.lastData();
    if (!last) return 'Unknown';

    const rate = this.calculateRate(); // % per hour

    if (rate > 0.05) return 'Infinite (Charging)';
    if (Math.abs(rate) <= 0.05) return 'Stable';

    // Respect 10% shutdown limit
    const usablePercentage = Math.max(0, last.percentage - 10);
    if (usablePercentage <= 0) return 'Shutdown Imminent';

    const hoursLeft = usablePercentage / Math.abs(rate);
    if (hoursLeft < 1) {
      const minutesLeft = Math.round(hoursLeft * 60);
      return `${minutesLeft}m remaining`;
    }
    return `${Math.floor(hoursLeft)}h remaining`;
  });
  public readonly timeToFull = computed(() => {
    const last = this.lastData();
    if (!last) return 'N/A';

    const rate = this.calculateRate(); // % per hour

    // Respect 80% capping limit
    const needed = 80 - last.percentage;
    if (needed <= 0) return 'Capped at 80%';

    if (rate <= 0.05) return 'N/A (Not Charging)';

    const hours = needed / rate;
    if (hours < 1) {
      const mins = Math.round(hours * 60);
      return `${mins}m to go`;
    }
    return `${hours.toFixed(1)}h to go`;
  });
  private readonly http = inject(HttpClient);
  private readonly configService = inject(ConfigService);
  // Data points signal
  private dataPoints = signal<BatteryData[]>([]);
  // Publicly accessible data
  public readonly allData = this.dataPoints.asReadonly();
  public readonly lastData = computed(() => {
    const data = this.dataPoints();
    return data.length > 0 ? data[data.length - 1] : null;
  });
  public readonly dailyHarvest = computed(() => {
    const data = this.dataPoints();
    if (data.length < 2) return 0;

    // Calculate total percentage gain across all data points
    // 10Ah battery at (approx) 4V = 40Wh total capacity.
    // 1% of 10Ah is 0.1Ah. 0.1Ah * 4V = 0.4Wh.
    // However, user said 10Ah, let's assume 3.7V average -> 37Wh for 100%.
    // So 1% = 0.37Wh.
    
    let totalGainPerc = 0;
    for (let i = 1; i < data.length; i++) {
      const diff = data[i].percentage - data[i - 1].percentage;
      if (diff > 0) {
        totalGainPerc += diff;
      }
    }

    // Using 3.7V * 10Ah = 37Wh capacity
    const whPerPercent = 0.37;
    return Math.round(totalGainPerc * whPerPercent);
  });

  constructor() {
    this.configService.getBatteryDataInterval$().pipe(
      switchMap(minutes => timer(0, minutes * 60 * 1000)),
      switchMap(() => this.configService.getBatteryDataUrl$()),
      switchMap(url => this.http.get<BatteryData[]>(url))
    ).subscribe({
      next: (parsedData) => {
        this.dataPoints.set(parsedData);
      },
      error: (err) => console.error('Failed to fetch battery data', err)
    });
  }

  private calculateRate(): number {
    const data = this.dataPoints();
    if (data.length < 2) return 0;

    // Use up to last 5 points to determine trend
    const recentPoints = data.slice(-5);
    const first = recentPoints[0];
    const last = recentPoints[recentPoints.length - 1];

    const timeDiffMs = new Date(last.timestamp).getTime() - new Date(first.timestamp).getTime();
    const percDiff = last.percentage - first.percentage;

    if (timeDiffMs === 0) return 0;

    // Return percentage change per hour
    return (percDiff / timeDiffMs) * 1000 * 60 * 60;
  }
}
