"""
Three.js 3D WebGL City & Traffic Animation Component
====================================================
Renders an interactive, futuristic 3D city with animated 3D vehicles,
traffic light signals, dynamic lighting, weather particle systems,
and real-time camera controls using Three.js and WebGL.
"""

import streamlit as st
import streamlit.components.v1 as components


def render_three_js_city(
    vehicle_density: int = 30,
    speed_factor: float = 1.0,
    weather: str = "Clear",
    night_mode: bool = True,
    show_traffic_lights: bool = True,
    height: int = 600
):
    """
    Renders an interactive Three.js 3D City Simulation HTML container inside Streamlit.
    """
    rain_active = "Rain" in weather or "Storm" in weather
    fog_active = "Fog" in weather or "Storm" in weather

    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ overflow: hidden; background: #050816; font-family: 'Inter', 'Segoe UI', Tahoma, sans-serif; }}
            #canvas-container {{ width: 100vw; height: {height}px; position: relative; }}
            #hud {{
                position: absolute;
                top: 15px;
                left: 15px;
                background: rgba(10, 15, 30, 0.88);
                border: 1px solid rgba(0, 217, 255, 0.35);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5), 0 0 20px rgba(0, 217, 255, 0.1);
                border-radius: 14px;
                padding: 14px 20px;
                color: #E2E8F0;
                font-size: 12px;
                pointer-events: none;
                z-index: 10;
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
            }}
            .hud-title {{ font-weight: 700; color: #00D9FF; text-transform: uppercase; font-size: 11px; letter-spacing: 1.5px; margin-bottom: 8px; text-shadow: 0 0 10px rgba(0,217,255,0.3); }}
            .hud-stat {{ display: flex; justify-content: space-between; gap: 15px; margin-top: 5px; }}
            .hud-val {{ font-weight: 600; color: #00FF8C; font-family: 'JetBrains Mono', monospace; }}
            
            #cam-controls {{
                position: absolute;
                bottom: 15px;
                right: 15px;
                display: flex;
                gap: 8px;
                z-index: 10;
            }}
            .cam-btn {{
                background: rgba(10, 15, 30, 0.88);
                backdrop-filter: blur(16px);
                border: 1px solid rgba(0, 217, 255, 0.3);
                color: #00D9FF;
                padding: 8px 14px;
                border-radius: 10px;
                cursor: pointer;
                font-size: 11px;
                font-weight: 600;
                transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
                letter-spacing: 0.3px;
            }}
            .cam-btn:hover {{
                background: linear-gradient(135deg, #00D9FF, #0088CC);
                color: #050816;
                box-shadow: 0 0 20px rgba(0, 217, 255, 0.4);
                transform: translateY(-2px);
                border-color: #00D9FF;
            }}
        </style>

        <!-- Three.js and OrbitControls -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>
        <div id="canvas-container">
            <div id="hud">
                <div class="hud-title">🌐 3D DIGITAL TWIN SIMULATOR</div>
                <div class="hud-stat"><span>Active Vehicles:</span><span class="hud-val" id="hud-vehicles">{vehicle_density}</span></div>
                <div class="hud-stat"><span>Target Speed:</span><span class="hud-val">{speed_factor:.1f}x</span></div>
                <div class="hud-stat"><span>Weather Condition:</span><span class="hud-val" style="color: #FFB300;">{weather}</span></div>
                <div class="hud-stat"><span>FPS:</span><span class="hud-val" id="hud-fps">60</span></div>
            </div>

            <div id="cam-controls">
                <button class="cam-btn" onclick="setPresetView('isometric')">📷 Free Orbit</button>
                <button class="cam-btn" onclick="setPresetView('topdown')">🗺️ Overhead Grid</button>
                <button class="cam-btn" onclick="setPresetView('chase')">🏎️ Chase Cam</button>
            </div>
        </div>

        <script>
            // --- Three.js Setup ---
            const container = document.getElementById('canvas-container');
            const scene = new THREE.Scene();
            
            const bgColor = { "true" if night_mode else "false" } ? 0x090D1C : 0x87CEEB;
            scene.background = new THREE.Color(bgColor);
            
            if ({ "true" if fog_active else "false" }) {{
                scene.fog = new THREE.FogExp2(0x090D1C, 0.015);
            }}

            const camera = new THREE.PerspectiveCamera(45, window.innerWidth / {height}, 1, 1000);
            camera.position.set(120, 100, 120);

            const renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(container.clientWidth, {height});
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            container.appendChild(renderer.domElement);

            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.maxPolarAngle = Math.PI / 2.05;

            // --- Lighting ---
            const ambientLight = new THREE.AmbientLight(0xffffff, { "0.4" if night_mode else "0.9" });
            scene.add(ambientLight);

            const dirLight = new THREE.DirectionalLight({ "0x00E5FF" if night_mode else "0xffffff" }, { "0.8" if night_mode else "1.2" });
            dirLight.position.set(100, 150, 50);
            dirLight.castShadow = true;
            scene.add(dirLight);

            // --- City Grid Generation ---
            const GRID_SIZE = 8;
            const BLOCK_SIZE = 30;
            const ROAD_WIDTH = 12;

            // Ground Plane
            const groundGeo = new THREE.PlaneGeometry(350, 350);
            const groundMat = new THREE.MeshStandardMaterial({{ color: 0x050814, roughness: 0.8 }});
            const ground = new THREE.Mesh(groundGeo, groundMat);
            ground.rotation.x = -Math.PI / 2;
            ground.receiveShadow = true;
            scene.add(ground);

            // Roads Network
            const roadMat = new THREE.MeshStandardMaterial({{ color: 0x111827, roughness: 0.5 }});
            const lineMat = new THREE.MeshBasicMaterial({{ color: 0x00E5FF }});

            // Draw roads and buildings
            const buildings = [];
            const buildingGeo = new THREE.BoxGeometry(1, 1, 1);

            for (let i = -GRID_SIZE/2; i < GRID_SIZE/2; i++) {{
                for (let j = -GRID_SIZE/2; j < GRID_SIZE/2; j++) {{
                    const x = i * (BLOCK_SIZE + ROAD_WIDTH);
                    const z = j * (BLOCK_SIZE + ROAD_WIDTH);

                    // Buildings
                    const bHeight = Math.random() * 45 + 15;
                    const bWidth = BLOCK_SIZE - 4;
                    const bDepth = BLOCK_SIZE - 4;

                    const hue = Math.random() > 0.5 ? 0x1E293B : 0x0F172A;
                    const bMat = new THREE.MeshStandardMaterial({{
                        color: hue,
                        metalness: 0.3,
                        roughness: 0.4
                    }});

                    const building = new THREE.Mesh(buildingGeo, bMat);
                    building.position.set(x + BLOCK_SIZE/2, bHeight/2, z + BLOCK_SIZE/2);
                    building.scale.set(bWidth, bHeight, bDepth);
                    building.castShadow = true;
                    building.receiveShadow = true;
                    scene.add(building);

                    // Neon Rooftop Accent
                    const roofGeo = new THREE.BoxGeometry(bWidth * 0.9, 1, bDepth * 0.9);
                    const roofMat = new THREE.MeshBasicMaterial({{ color: Math.random() > 0.5 ? 0x00E5FF : 0x7C4DFF }});
                    const roof = new THREE.Mesh(roofGeo, roofMat);
                    roof.position.set(x + BLOCK_SIZE/2, bHeight + 0.5, z + BLOCK_SIZE/2);
                    scene.add(roof);
                }}
            }}

            // Add Road Lines
            for (let k = -200; k <= 200; k += 42) {{
                const roadH = new THREE.Mesh(new THREE.PlaneGeometry(400, ROAD_WIDTH), roadMat);
                roadH.rotation.x = -Math.PI / 2;
                roadH.position.set(0, 0.1, k);
                scene.add(roadH);

                const roadV = new THREE.Mesh(new THREE.PlaneGeometry(ROAD_WIDTH, 400), roadMat);
                roadV.rotation.x = -Math.PI / 2;
                roadV.position.set(k, 0.1, 0);
                scene.add(roadV);
            }}

            // --- 3D Vehicles System ---
            const vehicles = [];
            const carColors = [0x00E5FF, 0x00E676, 0xFF1744, 0xFFC400, 0x7C4DFF];
            const carCount = Math.min({vehicle_density}, 80);

            for (let v = 0; v < carCount; v++) {{
                const carGroup = new THREE.Group();

                // Chassis
                const carMat = new THREE.MeshStandardMaterial({{
                    color: carColors[v % carColors.length],
                    metalness: 0.6,
                    roughness: 0.2
                }});
                const carBody = new THREE.Mesh(new THREE.BoxGeometry(3.5, 1.6, 7), carMat);
                carBody.position.y = 1.0;
                carBody.castShadow = true;
                carGroup.add(carBody);

                // Headlights
                const lightMat = new THREE.MeshBasicMaterial({{ color: 0xFFFFFF }});
                const hlLeft = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.4, 0.2), lightMat);
                hlLeft.position.set(-1.1, 1.0, 3.5);
                const hlRight = hlLeft.clone();
                hlRight.position.x = 1.1;
                carGroup.add(hlLeft);
                carGroup.add(hlRight);

                // Taillights
                const tailMat = new THREE.MeshBasicMaterial({{ color: 0xFF1744 }});
                const tlLeft = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.4, 0.2), tailMat);
                tlLeft.position.set(-1.1, 1.0, -3.5);
                const tlRight = tlLeft.clone();
                tlRight.position.x = 1.1;
                carGroup.add(tlLeft);
                carGroup.add(tlRight);

                // Position on road loop
                const laneOffset = (v % 2 === 0 ? 1 : -1) * 3.5;
                const axis = v % 2 === 0 ? 'X' : 'Z';
                const roadIndex = (v % 5 - 2) * 42;

                carGroup.position.set(
                    axis === 'X' ? (Math.random() * 300 - 150) : roadIndex + laneOffset,
                    0,
                    axis === 'Z' ? (Math.random() * 300 - 150) : roadIndex + laneOffset
                );

                carGroup.userData = {{
                    axis: axis,
                    direction: (v % 4 < 2 ? 1 : -1),
                    speed: (0.4 + Math.random() * 0.4) * {speed_factor},
                    laneOffset: laneOffset
                }};

                if (axis === 'X' && carGroup.userData.direction === -1) carGroup.rotation.y = Math.PI;
                if (axis === 'Z') carGroup.rotation.y = carGroup.userData.direction === 1 ? Math.PI/2 : -Math.PI/2;

                scene.add(carGroup);
                vehicles.push(carGroup);
            }}

            // --- Rain Particle System ---
            let rainParticles = null;
            if ({ "true" if rain_active else "false" }) {{
                const rainGeo = new THREE.BufferGeometry();
                const rainCount = 1500;
                const pos = new Float32Array(rainCount * 3);

                for (let r = 0; r < rainCount * 3; r += 3) {{
                    pos[r] = Math.random() * 400 - 200;
                    pos[r+1] = Math.random() * 150;
                    pos[r+2] = Math.random() * 400 - 200;
                }}

                rainGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
                const rainMat = new THREE.PointsMaterial({{
                    color: 0x00E5FF,
                    size: 0.8,
                    transparent: true,
                    opacity: 0.6
                }});
                rainParticles = new THREE.Points(rainGeo, rainMat);
                scene.add(rainParticles);
            }}

            // --- Traffic Lights ---
            let lightState = 'green';
            let lightTimer = 0;
            const signalLights = [];

            if ({ "true" if show_traffic_lights else "false" }) {{
                const postGeo = new THREE.CylinderGeometry(0.3, 0.3, 10);
                const postMat = new THREE.MeshStandardMaterial({{ color: 0x334155 }});

                [-42, 0, 42].forEach(x => {{
                    [-42, 0, 42].forEach(z => {{
                        const post = new THREE.Mesh(postGeo, postMat);
                        post.position.set(x + 8, 5, z + 8);
                        scene.add(post);

                        const lampGeo = new THREE.SphereGeometry(0.8, 16, 16);
                        const lampMat = new THREE.MeshBasicMaterial({{ color: 0x00E676 }});
                        const lamp = new THREE.Mesh(lampGeo, lampMat);
                        lamp.position.set(x + 8, 10, z + 8);
                        scene.add(lamp);
                        signalLights.push(lamp);
                    }});
                }});
            }}

            // --- Camera Presets ---
            window.setPresetView = function(type) {{
                if (type === 'isometric') {{
                    camera.position.set(120, 100, 120);
                    controls.target.set(0, 0, 0);
                }} else if (type === 'topdown') {{
                    camera.position.set(0, 220, 0.1);
                    controls.target.set(0, 0, 0);
                }} else if (type === 'chase' && vehicles.length > 0) {{
                    const v = vehicles[0];
                    camera.position.set(v.position.x - 20, 15, v.position.z - 20);
                    controls.target.copy(v.position);
                }}
                controls.update();
            }};

            // --- Main Animation Loop ---
            let lastTime = performance.now();
            let frameCount = 0;
            const hudFps = document.getElementById('hud-fps');

            function animate() {{
                requestAnimationFrame(animate);

                // FPS Counter
                frameCount++;
                const now = performance.now();
                if (now - lastTime >= 1000) {{
                    if (hudFps) hudFps.innerText = frameCount;
                    frameCount = 0;
                    lastTime = now;
                }}

                // Traffic Light Cycle
                lightTimer += 0.01;
                if (lightTimer > 4.0) {{
                    lightTimer = 0;
                    lightState = lightState === 'green' ? 'red' : 'green';
                    const colorHex = lightState === 'green' ? 0x00E676 : 0xFF1744;
                    signalLights.forEach(l => l.material.color.setHex(colorHex));
                }}

                // Update Vehicle Positions
                vehicles.forEach(car => {{
                    const d = car.userData;
                    
                    // Stop if red light at intersection
                    let isBlocked = false;
                    if (lightState === 'red' && Math.abs(car.position.x % 42) < 6 && Math.abs(car.position.z % 42) < 6) {{
                        isBlocked = true;
                    }}

                    if (!isBlocked) {{
                        if (d.axis === 'X') {{
                            car.position.x += d.speed * d.direction;
                            if (car.position.x > 180) car.position.x = -180;
                            if (car.position.x < -180) car.position.x = 180;
                        }} else {{
                            car.position.z += d.speed * d.direction;
                            if (car.position.z > 180) car.position.z = -180;
                            if (car.position.z < -180) car.position.z = 180;
                        }}
                    }}
                }});

                // Update Rain Drops
                if (rainParticles) {{
                    const positions = rainParticles.geometry.attributes.position.array;
                    for (let p = 1; p < positions.length; p += 3) {{
                        positions[p] -= 2.5;
                        if (positions[p] < 0) positions[p] = 150;
                    }}
                    rainParticles.geometry.attributes.position.needsUpdate = true;
                }}

                controls.update();
                renderer.render(scene, camera);
            }}

            animate();

            // Resize Handler
            window.addEventListener('resize', () => {{
                camera.aspect = window.innerWidth / {height};
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, {height});
            }});
        </script>
    </body>
    </html>
    """

    components.html(html_code, height=height + 20)
