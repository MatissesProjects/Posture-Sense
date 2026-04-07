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

    const { pose, iris } = data;
    const w = canvas.width;
    const h = canvas.height;

    // Draw Pose Connections
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
