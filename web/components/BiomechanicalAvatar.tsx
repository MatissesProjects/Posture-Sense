"use client";

import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Text } from '@react-three/drei';
import * as THREE from 'three';

interface SpinalHeatmap {
  C7: number;
  T4: number;
  L5: number;
}

interface BiomechanicalAvatarProps {
  pose: Record<string, { x: number; y: number; z: number }>;
  heatmap?: SpinalHeatmap;
}

const Joint = ({ position, color = "#4ade80", size = 0.05 }: { position: [number, number, number], color?: string, size?: number }) => (
  <mesh position={position}>
    <sphereGeometry args={[size, 16, 16]} />
    <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.5} />
  </mesh>
);

const Bone = ({ start, end, color = "#4ade80" }: { start: [number, number, number], end: [number, number, number], color?: string }) => {
  const direction = new THREE.Vector3().subVectors(new THREE.Vector3(...end), new THREE.Vector3(...start));
  const length = direction.length();
  const midpoint = new THREE.Vector3().addVectors(new THREE.Vector3(...start), new THREE.Vector3(...end)).multiplyScalar(0.5);
  
  const quaternion = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), direction.clone().normalize());

  return (
    <mesh position={midpoint} quaternion={quaternion}>
      <cylinderGeometry args={[0.02, 0.02, length, 8]} />
      <meshStandardMaterial color={color} transparent opacity={0.6} />
    </mesh>
  );
};

const Vertebra = ({ position, stress, label }: { position: [number, number, number], stress: number, label: string }) => {
  const color = useMemo(() => {
    // Red to Yellow to Green heatmap (inverted: 1 is red, 0 is green)
    const hue = (1 - stress) * 120;
    return `hsl(${hue}, 100%, 50%)`;
  }, [stress]);

  return (
    <group position={position}>
      <mesh>
        <boxGeometry args={[0.08, 0.04, 0.06]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={stress * 2} />
      </mesh>
      <Text
        position={[0.15, 0, 0]}
        fontSize={0.04}
        color="white"
        anchorX="left"
        anchorY="middle"
      >
        {label}: {Math.round(stress * 100)}%
      </Text>
    </group>
  );
};

function Scene({ pose, heatmap }: BiomechanicalAvatarProps) {
  if (!pose || !pose.nose) return null;

  // Map normalized CV coordinates (0-1) to 3D scene space (-2 to 2)
  const mapCoord = (p: { x: number, y: number, z: number }): [number, number, number] => [
    (p.x - 0.5) * 4,
    (0.5 - p.y) * 4,
    -p.z * 2
  ];

  const joints = useMemo(() => {
    const pts: Record<string, [number, number, number]> = {};
    Object.entries(pose).forEach(([key, val]) => {
      pts[key] = mapCoord(val);
    });
    return pts;
  }, [pose]);

  // Derived spinal points
  const midShoulder = useMemo(() => {
    if (!joints.left_shoulder || !joints.right_shoulder) return null;
    return [
      (joints.left_shoulder[0] + joints.right_shoulder[0]) / 2,
      (joints.left_shoulder[1] + joints.right_shoulder[1]) / 2,
      (joints.left_shoulder[2] + joints.right_shoulder[2]) / 2,
    ] as [number, number, number];
  }, [joints]);

  const midHip = useMemo(() => {
    if (!joints.left_hip || !joints.right_hip) return null;
    return [
      (joints.left_hip[0] + joints.right_hip[0]) / 2,
      (joints.left_hip[1] + joints.right_hip[1]) / 2,
      (joints.left_hip[2] + joints.right_hip[2]) / 2,
    ] as [number, number, number];
  }, [joints]);

  return (
    <>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      
      {/* Grid helper for spatial reference */}
      <gridHelper args={[10, 10, 0x334155, 0x1e293b]} rotation={[Math.PI/2, 0, 0]} position={[0, 0, -1]} />

      {Object.entries(joints).map(([name, pos]) => (
        <Joint key={name} position={pos} />
      ))}

      {/* Basic Skeleton */}
      {joints.left_shoulder && joints.right_shoulder && <Bone start={joints.left_shoulder} end={joints.right_shoulder} />}
      {joints.left_shoulder && joints.left_elbow && <Bone start={joints.left_shoulder} end={joints.left_elbow} />}
      {joints.left_elbow && joints.left_wrist && <Bone start={joints.left_elbow} end={joints.left_wrist} />}
      {joints.right_shoulder && joints.right_elbow && <Bone start={joints.right_shoulder} end={joints.right_elbow} />}
      {joints.right_elbow && joints.right_wrist && <Bone start={joints.right_elbow} end={joints.right_wrist} />}
      {joints.left_hip && joints.right_hip && <Bone start={joints.left_hip} end={joints.right_hip} />}
      
      {/* Spine & Heatmap */}
      {midShoulder && midHip && (
        <>
          <Bone start={midShoulder} end={midHip} color="#6366f1" />
          
          {/* Vertebral stress points */}
          <Vertebra 
            position={[midShoulder[0], midShoulder[1], midShoulder[2]]} 
            stress={heatmap?.C7 || 0} 
            label="C7 (Cervical)" 
          />
          <Vertebra 
            position={[midShoulder[0], (midShoulder[1] + midHip[1]) / 2, (midShoulder[2] + midHip[2]) / 2]} 
            stress={heatmap?.T4 || 0} 
            label="T4 (Thoracic)" 
          />
          <Vertebra 
            position={[midHip[0], midHip[1], midHip[2]]} 
            stress={heatmap?.L5 || 0} 
            label="L5 (Lumbar)" 
          />
        </>
      )}

      {/* Neck */}
      {joints.nose && midShoulder && <Bone start={joints.nose} end={midShoulder} color="#6366f1" />}

      <OrbitControls enablePan={true} enableZoom={true} makeDefault />
    </>
  );
}

export default function BiomechanicalAvatar({ pose, heatmap }: BiomechanicalAvatarProps) {
  return (
    <div className="w-full h-full bg-slate-950 rounded-xl border border-slate-800 shadow-inner overflow-hidden">
      <Canvas>
        <PerspectiveCamera makeDefault position={[0, 0, 5]} />
        <Scene pose={pose} heatmap={heatmap} />
      </Canvas>
      <div className="absolute bottom-4 left-4 bg-slate-900/80 backdrop-blur-md p-2 rounded border border-slate-700 pointer-events-none">
        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">3D Biomechanical Stress Model</p>
      </div>
    </div>
  );
}
