import React, { useRef, useMemo, useEffect } from 'react'
import { Canvas, useFrame, extend, ReactThreeFiber } from '@react-three/fiber'
import { Sphere, shaderMaterial, Sparkles, Float, Trail } from '@react-three/drei'
import * as THREE from 'three'

interface AdvancedOrbProps {
    state: "idle" | "listening" | "authorized" | "error"
}

// --------------------------------------------------------
// Custom Plasma Shader Material
// --------------------------------------------------------
const PlasmaMaterial = shaderMaterial(
    {
        uTime: 0,
        uColor1: new THREE.Color('#00ffff'), // Cyan
        uColor2: new THREE.Color('#ff00ff'), // Magenta
        uColor3: new THREE.Color('#ffffff'), // White Core
        uIntensity: 1.0,
        uSpeed: 0.5,
        uNoiseStrength: 0.2
    },
    // Vertex Shader
    `
    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vPosition;
    uniform float uTime;
    uniform float uSpeed;
    uniform float uNoiseStrength;

    // Simple noise function
    float random(vec3 scale, float seed) {
        return fract(sin(dot(gl_Position.xyz + seed, scale)) * 43758.5453 + seed);
    }

    void main() {
        vUv = uv;
        vNormal = normalize(normalMatrix * normal);
        vPosition = position;
        
        // Displace vertices for "wobble"
        vec3 pos = position;
        float displacement = sin(pos.x * 3.0 + uTime * uSpeed) * cos(pos.y * 4.0 + uTime * uSpeed) * uNoiseStrength;
        pos += normal * displacement;

        gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
    }
    `,
    // Fragment Shader
    `
    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vPosition;
    uniform float uTime;
    uniform vec3 uColor1;
    uniform vec3 uColor2;
    uniform vec3 uColor3;
    uniform float uIntensity;

    void main() {
        // dynamic flowing ribbons
        float time = uTime * 0.5;
        
        // Create ribbon pattern using sin waves
        float pattern = sin(vPosition.y * 10.0 + time * 2.0 + sin(vPosition.x * 10.0 + time));
        float pattern2 = cos(vPosition.x * 15.0 - time * 1.5 + cos(vPosition.z * 10.0));
        
        // Combine patterns for "intertwined" look
        float ribbon = step(0.8, sin(pattern * pattern2 * 4.0));
        
        // Soft glow edges for ribbons
        float glow = smoothstep(0.0, 1.0, sin(pattern * pattern2 * 4.0));

        // Fresnel effect for rim lighting
        float fresnel = pow(1.0 - abs(dot(vNormal, vec3(0.0, 0.0, 1.0))), 3.0);

        // Mix colors based on pattern position
        vec3 baseColor = mix(uColor1, uColor2, vUv.y + sin(time));
        vec3 finalColor = baseColor * glow * 1.5;
        
        // Add core hot spots
        finalColor += uColor3 * pow(glow, 4.0) * 2.0;
        
        // Add fresnel rim
        finalColor += uColor1 * fresnel * 2.0;

        // Apply intensity
        finalColor *= uIntensity;

        // Transparency logic - keep ribbons opaque, space transparent
        float alpha = glow * 0.8 + fresnel * 0.4;
        
        gl_FragColor = vec4(finalColor, alpha);
    }
    `
)

extend({ PlasmaMaterial })

// Add type definition for the custom material
declare global {
    namespace JSX {
        interface IntrinsicElements {
            plasmaMaterial: ReactThreeFiber.Object3DNode<THREE.ShaderMaterial, typeof PlasmaMaterial> & {
                uTime?: number
                uColor1?: THREE.Color
                uColor2?: THREE.Color
                uColor3?: THREE.Color
                uIntensity?: number
                uSpeed?: number
                uNoiseStrength?: number
            }
        }
    }
}

// --------------------------------------------------------
// Background "Fake" Bloom Layer
// --------------------------------------------------------
function GlowLayer({ color, scale, intensity }: { color: string, scale: number, intensity: number }) {
    return (
        <mesh scale={scale}>
            <sphereGeometry args={[1, 32, 32]} />
            <meshBasicMaterial
                color={color}
                transparent
                opacity={0.15 * intensity}
                blending={THREE.AdditiveBlending}
                side={THREE.BackSide} // Render on inside to avoid occlusion issues with main orb
                depthWrite={false}
            />
        </mesh>
    )
}

// --------------------------------------------------------
// Main Orb Component
// --------------------------------------------------------
function VortexOrb({ state }: { state: AdvancedOrbProps['state'] }) {
    const materialRef = useRef<any>(null)
    const meshRef = useRef<THREE.Mesh>(null)

    // Config based on state
    const config = useMemo(() => {
        switch (state) {
            case 'listening':
                return {
                    speed: 2.5,
                    intensity: 2.0,
                    noise: 0.3,
                    color1: '#4ade80', // Bright Green
                    color2: '#2dd4bf', // Teal
                    scale: 1.15
                }
            case 'authorized':
                return {
                    speed: 5.0,
                    intensity: 3.0,
                    noise: 0.5,
                    color1: '#10b981', // Emerald
                    color2: '#fbbf24', // Amber hint
                    scale: 1.3
                }
            case 'error':
                return {
                    speed: 2.0,
                    intensity: 1.5,
                    noise: 0.8,
                    color1: '#ef4444',
                    color2: '#7f1d1d',
                    scale: 0.95
                }
            case 'idle':
            default:
                return {
                    speed: 1.0,
                    intensity: 1.0,
                    noise: 0.1, // Very smooth
                    color1: '#059669', // Emerald 600
                    color2: '#047857', // Emerald 700
                    scale: 1.0
                }
        }
    }, [state])

    useFrame((state, delta) => {
        if (materialRef.current) {
            materialRef.current.uTime += delta * config.speed

            // Lerp values for smooth transitions
            materialRef.current.uIntensity = THREE.MathUtils.lerp(materialRef.current.uIntensity, config.intensity, 0.05)
            materialRef.current.uSpeed = THREE.MathUtils.lerp(materialRef.current.uSpeed, config.speed, 0.05)
            materialRef.current.uNoiseStrength = THREE.MathUtils.lerp(materialRef.current.uNoiseStrength, config.noise, 0.05)

            materialRef.current.uColor1.lerp(new THREE.Color(config.color1), 0.05)
            materialRef.current.uColor2.lerp(new THREE.Color(config.color2), 0.05)
        }

        if (meshRef.current) {
            // Constant rotation
            meshRef.current.rotation.y += delta * 0.2 * config.speed
            meshRef.current.rotation.z += delta * 0.1 * config.speed

            // Breathing scale
            const breath = Math.sin(state.clock.elapsedTime * 2) * 0.05
            const targetScale = config.scale + breath
            meshRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.05)
        }
    })

    return (
        <group>
            {/* Main Plasma Sphere */}
            <mesh ref={meshRef}>
                <sphereGeometry args={[1, 128, 128]} />
                <plasmaMaterial
                    ref={materialRef}
                    transparent
                    side={THREE.DoubleSide}
                    blending={THREE.AdditiveBlending}
                    depthWrite={false} // Important for internal transparency look
                />
            </mesh>

            {/* Inner Core Glow (White Hot) */}
            <mesh scale={0.6}>
                <sphereGeometry args={[1, 32, 32]} />
                <meshBasicMaterial
                    color="#ffffff"
                    transparent
                    opacity={state === 'authorized' ? 0.8 : 0.4}
                    blending={THREE.AdditiveBlending}
                />
            </mesh>

            {/* Outer Glow Layers (Fake Bloom) */}
            <GlowLayer color={config.color1} scale={1.2} intensity={config.intensity} />
            <GlowLayer color={config.color2} scale={1.4} intensity={config.intensity * 0.5} />
        </group>
    )
}

// --------------------------------------------------------
// Dynamic Trails System
// --------------------------------------------------------
function OrbitingTrails({ state }: { state: AdvancedOrbProps['state'] }) {
    const groupRef = useRef<THREE.Group>(null)
    const isHighEnergy = state === 'listening' || state === 'authorized'

    useFrame((state, delta) => {
        if (groupRef.current) {
            groupRef.current.rotation.y += delta * (isHighEnergy ? 2 : 0.5)
            groupRef.current.rotation.x += delta * (isHighEnergy ? 1 : 0.2)
        }
    })

    return (
        <group ref={groupRef}>
            {/* Render several trails with different orbits */}
            {[...Array(6)].map((_, i) => (
                <Float key={i} speed={isHighEnergy ? 5 : 2} rotationIntensity={isHighEnergy ? 4 : 2} floatIntensity={1}>
                    <mesh position={[2, 0, 0]} scale={0.05}>
                        <sphereGeometry args={[1, 16, 16]} />
                        <meshBasicMaterial color={state === 'authorized' ? '#fbbf24' : '#34d399'} />
                    </mesh>
                    {/* Trail doesn't render well in all R3F versions without specific setup, using simple mesh trail if Trail component fails or just Sparkles in trail */}
                    <Sparkles
                        count={20}
                        scale={4}
                        size={isHighEnergy ? 6 : 3}
                        speed={isHighEnergy ? 2 : 0.4}
                        opacity={isHighEnergy ? 0.8 : 0.4}
                        color={state === 'error' ? '#ef4444' : '#4ade80'}
                    />
                </Float>
            ))}
        </group>
    )
}


export function AdvancedOrb({ state }: AdvancedOrbProps) {
    return (
        <div className="w-full h-full">
            <Canvas camera={{ position: [0, 0, 4], fov: 50 }} gl={{ alpha: true, antialias: true }}>
                {/* No lights needed for additive shader, but ambient helps sparkles */}
                <ambientLight intensity={0.5} />

                <VortexOrb state={state} />
                <OrbitingTrails state={state} />

                {state === 'authorized' && (
                    <Sparkles count={200} scale={6} size={10} speed={4} color="#ffd700" />
                )}
            </Canvas>
        </div>
    )
}
