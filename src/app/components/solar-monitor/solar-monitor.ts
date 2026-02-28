import {Component, computed, inject, signal} from '@angular/core';
import {DecimalPipe} from '@angular/common';
import {BatteryData, SolarService} from "../../services/solar-service";

@Component({
  selector: 'solar-monitor',
  templateUrl: './solar-monitor.html',
  styleUrl: './solar-monitor.scss',
  standalone: true,
  imports: [DecimalPipe]
})
export class SolarMonitor {
  // Signal for collapsed state
  protected isCollapsed = signal(true);
  protected batteryPoints = computed(() => {
    return this.generatePoints(d => d.percentage, 0, 100);
  });
  protected solarPoints = computed(() => {
    return this.generatePoints(d => d.solar_radiation_Wm2, 0, 1000);
  });
  private readonly solarService = inject(SolarService);
  // Expose service data to template
  protected lastData = this.solarService.lastData;
  protected efficiency = this.solarService.efficiency;
  protected isCharging = this.solarService.isCharging;
  protected estimatedUptime = this.solarService.estimatedUptime;
  protected timeToFull = this.solarService.timeToFull;
  protected dailyHarvest = this.solarService.dailyHarvest;

  toggleCollapse() {
    this.isCollapsed.set(!this.isCollapsed());
  }

  private generatePoints(accessor: (d: BatteryData) => number, min: number, max: number): string {
    const data = this.solarService.allData();
    if (data.length < 2) return '';
    const width = 400;
    const height = 100;
    const step = width / (data.length - 1);
    
    return data.map((d, i) => {
      const x = i * step;
      const val = accessor(d);
      const y = height - ((val - min) / (max - min)) * height;
      return `${x},${y}`;
    }).join(' ');
  }
}
