"use client";

import React, { useEffect, useRef, useState } from 'react';

interface Landmark {
  x: number;
  y: number;
  z: number;
  visibility?: number;
}

interface PostureData {
  pose: Record<string, Landmark>;
  iris: {
    left: Landmark[];
    right: Landmark[];
  };
  analysis: {
    score: number;
    is_standing: boolean;
    calibrated: boolean;
    feedback: string;
    metrics: Record<string, number>;
  };
  resolution: {
    width: number;
    height: number;
  };
}

export default function PostureCanvas({ onData }: { onData?: (data: PostureData) => void }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    // Connect to WebSocket using 127.0.0.1 for better reliability
    const socket = new WebSocket('ws://127.0.0.1:8000/ws/posture');
    socketRef.current = socket;

    socket.onopen = () => {
      setConnected(true);
      console.log('WebSocket Connected');
    };

    socket.onclose = () => {
      setConnected(false);
      console.log('WebSocket Disconnected');
    };

    socket.onmessage = (event) => {
      try {
        const data: PostureData = JSON.parse(event.data);
        if (onData) onData(data);
        drawSkeleton(data);
      } catch (err) {
        // console.error('Error parsing WS message', err);
      }
    };

    return () => {
      socket.close();
    };
  }, []);

  const drawSkeleton = (data: PostureData) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const { pose, iris, analysis } = data;
    const w = canvas.width;
    const h = canvas.height;

    // --- Draw Virtual Monitors (Back-projected) ---
    if (data.workspace && data.workspace.monitors && data.workspace.webcam_global_pos) {
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
      ctx.lineWidth = 1;
      const { monitors, webcam_global_pos, mirror_mode } = data.workspace;
      const camViewCenter = { x: 0.5, y: 0.5 };

      monitors.forEach((m: any) => {
        const projScale = 0.0004; 
        
        let relX = (m.x - webcam_global_pos.x) * projScale;
        const relY = (m.y - webcam_global_pos.y) * projScale;
        const mW = m.width * projScale;
        const mH = m.height * projScale;

        // Flip X if mirrored
        if (mirror_mode) {
          relX = -relX - mW;
        }

        const drawX = (camViewCenter.x + relX) * w;
        const drawY = (camViewCenter.y + relY) * h;
        const drawW = mW * w;
        const drawH = mH * h;

        ctx.strokeRect(drawX, drawY, drawW, drawH);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.05)';
        ctx.fillRect(drawX, drawY, drawW, drawH);
        
        ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
        ctx.font = '10px sans-serif';
        ctx.fillText(`M${m.id}`, drawX + 5, drawY + 15);
      });
    }

    // --- Draw Gaze Point ---
    if (analysis && analysis.gaze_point) {
      let { x, y } = analysis.gaze_point;
      const isMirrored = data.workspace?.mirror_mode;

      // Map normalized gaze (relative to eye) to full canvas
      // This is a rough projection for visualization
      // CLAMP coordinates to keep the crosshair visible
      const gazeX = Math.max(10, Math.min(w - 10, x * w));
      const gazeY = Math.max(10, Math.min(h - 10, y * h));

      ctx.strokeStyle = '#f43f5e'; // Rose-500
      ctx.lineWidth = 2;
      // Crosshair
      ctx.beginPath();
      ctx.moveTo(gazeX - 15, gazeY);
      ctx.lineTo(gazeX + 15, gazeY);
      ctx.moveTo(gazeX, gazeY - 15);
      ctx.lineTo(gazeX, gazeY + 15);
      ctx.stroke();
      
      ctx.fillStyle = '#f43f5e';
      ctx.beginPath();
      ctx.arc(gazeX, gazeY, 4, 0, 2 * Math.PI);
      ctx.fill();
    }

    // --- Draw Pose Connections ---
    ctx.strokeStyle = '#4ade80'; // Green-400
    ctx.lineWidth = 3;

    const connections = [
      ['left_shoulder', 'right_shoulder'],
      ['left_shoulder', 'left_elbow'],
      ['left_elbow', 'left_wrist'],
      ['right_shoulder', 'right_elbow'],
      ['right_elbow', 'right_wrist'],
      ['left_shoulder', 'left_hip'],
      ['right_shoulder', 'right_hip'],
      ['left_hip', 'right_hip']
    ];

    connections.forEach(([p1, p2]) => {
      if (pose[p1] && pose[p2]) {
        ctx.beginPath();
        ctx.moveTo(pose[p1].x * w, pose[p1].y * h);
        ctx.lineTo(pose[p2].x * w, pose[p2].y * h);
        ctx.stroke();
      }
    });

    // Draw Pose Landmarks
    ctx.fillStyle = '#22c55e'; // Green-500
    Object.values(pose).forEach((lm) => {
      ctx.beginPath();
      ctx.arc(lm.x * w, lm.y * h, 5, 0, 2 * Math.PI);
      ctx.fill();
    });

    // Draw Irises
    ctx.fillStyle = '#3b82f6'; // Blue-500
    if (iris) {
      [...iris.left, ...iris.right].forEach((lm) => {
        // Iris landmarks are already in pixel coordinates from the backend
        // We need to scale them based on the canvas size vs original resolution
        const scaleX = w / data.resolution.width;
        const scaleY = h / data.resolution.height;
        ctx.beginPath();
        ctx.arc(lm.x * scaleX, lm.y * scaleY, 2, 0, 2 * Math.PI);
        ctx.fill();
      });
    }
  };

  return (
    <div className="relative w-full aspect-video bg-slate-900 rounded-xl overflow-hidden shadow-2xl border border-slate-700">
      {!connected && (
        <div className="absolute inset-0 flex items-center justify-center bg-slate-900/80 z-10 text-white">
          <p className="animate-pulse">Connecting to Posture Engine...</p>
        </div>
      )}
      <canvas
        ref={canvasRef}
        width={640}
        height={480}
        className="w-full h-full object-contain"
      />
    </div>
  );
}
