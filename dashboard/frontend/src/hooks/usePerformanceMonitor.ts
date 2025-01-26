import { useEffect, useRef } from 'react';

interface PerformanceMetrics {
  renderTime: number;
  messageLatency: number;
  fps: number;
  memoryUsage?: number;
}

export const usePerformanceMonitor = (componentName: string) => {
  const metricsRef = useRef<PerformanceMetrics>({
    renderTime: 0,
    messageLatency: 0,
    fps: 0
  });

  const frameCountRef = useRef(0);
  const lastFrameTimeRef = useRef(performance.now());
  const startTimeRef = useRef(performance.now());

  useEffect(() => {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach((entry) => {
        if (entry.entryType === 'measure' && entry.name.startsWith(componentName)) {
          metricsRef.current.renderTime = entry.duration;
        }
      });
    });

    observer.observe({ entryTypes: ['measure'] });

    const calculateFPS = () => {
      const now = performance.now();
      const elapsed = now - lastFrameTimeRef.current;
      frameCountRef.current++;

      if (elapsed >= 1000) {
        metricsRef.current.fps = Math.round((frameCountRef.current * 1000) / elapsed);
        frameCountRef.current = 0;
        lastFrameTimeRef.current = now;
      }

      requestAnimationFrame(calculateFPS);
    };

    const frameId = requestAnimationFrame(calculateFPS);

    // Memory usage monitoring (if available)
    const memoryInterval = setInterval(() => {
      if ((performance as any).memory) {
        metricsRef.current.memoryUsage = (performance as any).memory.usedJSHeapSize / (1024 * 1024);
      }
    }, 5000);

    return () => {
      observer.disconnect();
      cancelAnimationFrame(frameId);
      clearInterval(memoryInterval);
    };
  }, [componentName]);

  const measureMessageLatency = (startTime: number) => {
    const latency = performance.now() - startTime;
    metricsRef.current.messageLatency = latency;
  };

  const startMeasure = () => {
    startTimeRef.current = performance.now();
    performance.mark(`${componentName}-start`);
  };

  const endMeasure = () => {
    performance.mark(`${componentName}-end`);
    performance.measure(
      `${componentName}-render`,
      `${componentName}-start`,
      `${componentName}-end`
    );
  };

  const getMetrics = (): PerformanceMetrics => {
    return { ...metricsRef.current };
  };

  return {
    startMeasure,
    endMeasure,
    measureMessageLatency,
    getMetrics
  };
}; 