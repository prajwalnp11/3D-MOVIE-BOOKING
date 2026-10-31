/**
 * CINEVERSE - 3D Interactive WebGL Cinema Auditorium
 * Built with Three.js, VideoTexture, and Django REST Framework
 */

import * as THREE from 'three';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/controls/OrbitControls.js';
import { RoundedBoxGeometry } from 'https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/geometries/RoundedBoxGeometry.js';

// ==========================================
// 1. STATE & DOM ELEMENTS
// ==========================================
const container = document.getElementById('theatre3D');
if (!container) {
    throw new Error('3D Auditorium container #theatre3D not found');
}

const currentShowtimeId = container.dataset.showtimeId;
const currentMovieTitle = container.dataset.movieTitle || 'CineVerse Feature';
const currentTrailerUrl = container.dataset.trailerUrl || '';
const currentVideoMp4 = container.dataset.videoMp4 || 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4';

// Selected Seats Store: key = seat.id -> seat data
export const selectedSeats = new Map();
export const addedSnacks = new Map(); // id -> { id, name, price, quantity, image }

let selectableSeats = [];
let seatMeshMap = new Map(); // seatId -> group
let showtimeData = null;
let videoElement = null;
let screenMesh = null;
let screenLight = null;
let cameraAnimation = null;
let isAudioMuted = true;

// Tooltip DOM Element
let tooltip = document.getElementById('seatTooltip');
if (!tooltip) {
    tooltip = document.createElement('div');
    tooltip.id = 'seatTooltip';
    tooltip.className = 'absolute z-40 hidden pointer-events-none px-3 py-1.5 rounded-xl bg-dark-950/90 backdrop-blur-md border border-neon/50 text-white text-xs font-mono shadow-neon transition-all duration-75';
    container.appendChild(tooltip);
}

// ==========================================
// 2. THREE.JS SCENE, CAMERA & RENDERER
// ==========================================
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x06070a);
scene.fog = new THREE.FogExp2(0x06070a, 0.025);

const camera = new THREE.PerspectiveCamera(
    46,
    container.clientWidth / container.clientHeight,
    0.1,
    100
);
// Default Overview Angle
camera.position.set(0, 10, 18);

const renderer = new THREE.WebGLRenderer({
    antialias: true,
    powerPreference: 'high-performance',
    alpha: false
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(container.clientWidth, container.clientHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;

container.innerHTML = '';
container.style.position = 'relative';
container.appendChild(renderer.domElement);
container.appendChild(tooltip);

// OrbitControls
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 2.5, -2);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.minDistance = 4;
controls.maxDistance = 28;
controls.maxPolarAngle = Math.PI / 2.05;
controls.minPolarAngle = Math.PI / 10;

// ==========================================
// 3. CINEMATIC LIGHTING
// ==========================================
// Ambient Hemisphere Light
const hemiLight = new THREE.HemisphereLight(0x1a233a, 0x070913, 1.2);
scene.add(hemiLight);

// Key Directional Ceiling Light
const ceilingLight = new THREE.DirectionalLight(0xfff3e0, 1.8);
ceilingLight.position.set(-4, 15, 6);
ceilingLight.castShadow = true;
ceilingLight.shadow.mapSize.set(1024, 1024);
ceilingLight.shadow.bias = -0.0001;
scene.add(ceilingLight);

// Dynamic Screen Projector Light (Simulates movie light bouncing into auditorium)
screenLight = new THREE.PointLight(0x00f0ff, 45, 24, 1.2);
screenLight.position.set(0, 5.5, -6.5);
scene.add(screenLight);

// Warm Fill Light at Back
const backFillLight = new THREE.PointLight(0xccff00, 12, 20);
backFillLight.position.set(0, 8, 8);
scene.add(backFillLight);

// ==========================================
// 4. FUTURISTIC MATERIALS PALETTE
// ==========================================
const materials = {
    carpet: new THREE.MeshStandardMaterial({
        color: 0x0f1118,
        roughness: 0.95,
        metalness: 0.05
    }),
    wall: new THREE.MeshStandardMaterial({
        color: 0x0c0d14,
        roughness: 0.85,
        metalness: 0.15
    }),
    ceiling: new THREE.MeshStandardMaterial({
        color: 0x08090d,
        roughness: 0.95
    }),
    acousticPanel: new THREE.MeshStandardMaterial({
        color: 0x141824,
        roughness: 0.8,
        metalness: 0.2
    }),
    neonStripCyan: new THREE.MeshBasicMaterial({
        color: 0x00f0ff
    }),
    neonStripLime: new THREE.MeshBasicMaterial({
        color: 0xccff00
    }),
    blackPlastic: new THREE.MeshStandardMaterial({
        color: 0x111318,
        roughness: 0.6,
        metalness: 0.2
    }),
    metalChrome: new THREE.MeshStandardMaterial({
        color: 0x8a92a5,
        metalness: 0.85,
        roughness: 0.25
    }),

    // Tier Seat Materials
    seatRoyal: new THREE.MeshStandardMaterial({
        color: 0x0284c7, // Neon Cyan / Royal Blue
        roughness: 0.55,
        metalness: 0.25,
        emissive: 0x02365c,
        emissiveIntensity: 0.25
    }),
    seatBalcony: new THREE.MeshStandardMaterial({
        color: 0x8b5cf6, // Neon Purple / Violet
        roughness: 0.65,
        metalness: 0.15,
        emissive: 0x3b1875,
        emissiveIntensity: 0.25
    }),
    seatPrime: new THREE.MeshStandardMaterial({
        color: 0x059669, // Neon Emerald / Green
        roughness: 0.65,
        metalness: 0.15,
        emissive: 0x064e3b,
        emissiveIntensity: 0.25
    }),
    seatClassic: new THREE.MeshStandardMaterial({
        color: 0x475569, // Slate Steel
        roughness: 0.75,
        metalness: 0.1
    }),
    seatBooked: new THREE.MeshStandardMaterial({
        color: 0x1e212b, // Dim Charcoal / Sold Out
        roughness: 0.9,
        metalness: 0.05
    }),

    // Selected Glowing Material
    seatSelected: new THREE.MeshStandardMaterial({
        color: 0xccff00, // Electric Lime Neon
        roughness: 0.35,
        metalness: 0.2,
        emissive: 0xccff00,
        emissiveIntensity: 0.85
    }),

    // Hover Highlight Material
    seatHover: new THREE.MeshStandardMaterial({
        color: 0xffffff,
        roughness: 0.3,
        emissive: 0x00f0ff,
        emissiveIntensity: 0.5
    })
};

// ==========================================
// 5. AUDITORIUM ARCHITECTURE & ROOM
// ==========================================
function buildAuditoriumRoom() {
    // Sloped Stadium Tier Floor
    const floorGeo = new THREE.BufferGeometry();
    floorGeo.setAttribute('position', new THREE.Float32BufferAttribute([
        -10, 0.0, -8,
         10, 0.0, -8,
        -10, 2.4,  9,
         10, 2.4,  9
    ], 3));
    floorGeo.setIndex([0, 2, 1, 1, 2, 3]);
    floorGeo.computeVertexNormals();

    const floorMesh = new THREE.Mesh(floorGeo, materials.carpet);
    floorMesh.receiveShadow = true;
    scene.add(floorMesh);

    // Side Walls
    const wallGeo = new THREE.BoxGeometry(0.3, 10, 20);
    const leftWall = new THREE.Mesh(wallGeo, materials.wall);
    leftWall.position.set(-10, 5, 0);
    leftWall.receiveShadow = true;
    scene.add(leftWall);

    const rightWall = new THREE.Mesh(wallGeo, materials.wall);
    rightWall.position.set(10, 5, 0);
    rightWall.receiveShadow = true;
    scene.add(rightWall);

    // Back Wall & Ceiling
    const backWall = new THREE.Mesh(new THREE.BoxGeometry(20, 10, 0.4), materials.wall);
    backWall.position.set(0, 5, 9.2);
    scene.add(backWall);

    const ceiling = new THREE.Mesh(new THREE.BoxGeometry(20, 0.3, 20), materials.ceiling);
    ceiling.position.set(0, 9.8, 0);
    scene.add(ceiling);

    // Glowing Neon Floor Aisle Runners
    const aisleRunnerGeo = new THREE.BoxGeometry(0.08, 0.03, 17);
    const leftAisle = new THREE.Mesh(aisleRunnerGeo, materials.neonStripCyan);
    leftAisle.position.set(-7.5, 1.2, 0.5);
    leftAisle.rotation.x = 0.14; // match slope
    scene.add(leftAisle);

    const rightAisle = new THREE.Mesh(aisleRunnerGeo, materials.neonStripCyan);
    rightAisle.position.set(7.5, 1.2, 0.5);
    rightAisle.rotation.x = 0.14;
    scene.add(rightAisle);

    // Futuristic Acoustic Wall Ribs with Alternating Neon Accents
    for (let i = 0; i < 9; i++) {
        const z = -6.5 + i * 1.7;
        const y = 4.2 + (i * 0.15);

        // Left panels
        const panelLeft = new THREE.Mesh(new THREE.BoxGeometry(0.12, 3.2, 1.1), materials.acousticPanel);
        panelLeft.position.set(-9.8, y, z);
        scene.add(panelLeft);

        // Right panels
        const panelRight = new THREE.Mesh(new THREE.BoxGeometry(0.12, 3.2, 1.1), materials.acousticPanel);
        panelRight.position.set(9.8, y, z);
        scene.add(panelRight);

        // Vertical Neon Sconces
        const stripMat = (i % 2 === 0) ? materials.neonStripCyan : materials.neonStripLime;
        const sconceL = new THREE.Mesh(new THREE.BoxGeometry(0.04, 2.6, 0.04), stripMat);
        sconceL.position.set(-9.7, y, z);
        scene.add(sconceL);

        const sconceR = new THREE.Mesh(new THREE.BoxGeometry(0.04, 2.6, 0.04), stripMat);
        sconceR.position.set(9.7, y, z);
        scene.add(sconceR);
    }
}

// ==========================================
// 6. FRONT VIRTUAL CINEMA SCREEN (VideoTexture)
// ==========================================
function setupCinemaScreen(videoUrl, title) {
    // Screen Frame Base
    const frameGeo = new THREE.BoxGeometry(13.2, 6.8, 0.4);
    const frameMesh = new THREE.Mesh(frameGeo, materials.blackPlastic);
    frameMesh.position.set(0, 5.2, -8.1);
    scene.add(frameMesh);

    // Gold/Neon Accent Frame Border
    const borderGeo = new THREE.BoxGeometry(13.4, 7.0, 0.1);
    const borderMesh = new THREE.Mesh(borderGeo, materials.neonStripCyan);
    borderMesh.position.set(0, 5.2, -8.15);
    scene.add(borderMesh);

    // Create Hidden HTML5 Video Element for VideoTexture
    videoElement = document.createElement('video');
    videoElement.src = videoUrl;
    videoElement.crossOrigin = 'anonymous';
    videoElement.loop = true;
    videoElement.muted = true;
    videoElement.playsInline = true;
    videoElement.autoplay = true;

    // Start video playback
    videoElement.play().catch(err => {
        console.warn('VideoTexture autoplay waiting for user interaction:', err);
    });

    // Create Three.js VideoTexture
    const videoTexture = new THREE.VideoTexture(videoElement);
    videoTexture.colorSpace = THREE.SRGBColorSpace;
    videoTexture.minFilter = THREE.LinearFilter;
    videoTexture.magFilter = THREE.LinearFilter;

    // Slightly Curved Cinema Screen Mesh
    const screenGeo = new THREE.PlaneGeometry(12.8, 6.4, 24, 1);
    
    // Apply slight curve along X for immersive cinema feel
    const pos = screenGeo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
        const x = pos.getX(i);
        pos.setZ(i, -Math.pow(x / 6.4, 2) * 0.45);
    }
    screenGeo.computeVertexNormals();

    const screenMat = new THREE.MeshBasicMaterial({
        map: videoTexture,
        toneMapped: false
    });

    screenMesh = new THREE.Mesh(screenGeo, screenMat);
    screenMesh.position.set(0, 5.2, -7.8);
    scene.add(screenMesh);

    // Screen Speaker Grill Bottom
    const speakerMesh = new THREE.Mesh(new THREE.BoxGeometry(12.8, 0.4, 0.2), materials.metalChrome);
    speakerMesh.position.set(0, 1.8, -7.9);
    scene.add(speakerMesh);
}

// ==========================================
// 7. 3D PROCEDURAL SEAT MESH BUILDER
// ==========================================
function getTierMaterial(category) {
    switch (category) {
        case 'ROYAL':
        case 'RECLINER':
            return materials.seatRoyal;
        case 'BALCONY':
            return materials.seatBalcony;
        case 'PRIME':
        case 'PREMIUM':
            return materials.seatPrime;
        case 'CLASSIC':
        default:
            return materials.seatClassic;
    }
}

function createSeatMesh(seatData) {
    const { id, row, number, category, price, x, y, z, is_booked } = seatData;
    const group = new THREE.Group();

    const isRecliner = category === 'ROYAL' || category === 'RECLINER';
    const baseMat = is_booked ? materials.seatBooked : getTierMaterial(category);

    // Cushion
    const cushion = new THREE.Mesh(
        new RoundedBoxGeometry(isRecliner ? 0.98 : 0.86, 0.28, 0.86, 3, 0.08),
        baseMat
    );
    cushion.position.set(0, 0.82, 0.02);
    cushion.castShadow = true;
    cushion.receiveShadow = true;
    group.add(cushion);

    // Backrest
    const backrestHeight = isRecliner ? 1.3 : 1.05;
    const backrest = new THREE.Mesh(
        new RoundedBoxGeometry(isRecliner ? 0.98 : 0.86, backrestHeight, 0.26, 3, 0.08),
        baseMat
    );
    backrest.position.set(0, 1.45, 0.38);
    backrest.rotation.x = isRecliner ? -0.14 : -0.08;
    backrest.castShadow = true;
    backrest.receiveShadow = true;
    group.add(backrest);

    // Headrest
    const headrest = new THREE.Mesh(
        new RoundedBoxGeometry(isRecliner ? 0.65 : 0.54, 0.3, 0.22, 3, 0.08),
        baseMat
    );
    headrest.position.set(0, isRecliner ? 2.15 : 1.95, 0.32);
    group.add(headrest);

    // Armrests with Neon Cupholders
    for (const side of [-1, 1]) {
        const armWidth = isRecliner ? 0.2 : 0.15;
        const armX = side * (isRecliner ? 0.58 : 0.5);

        const arm = new THREE.Mesh(
            new RoundedBoxGeometry(armWidth, 0.36, 0.88, 3, 0.05),
            materials.blackPlastic
        );
        arm.position.set(armX, 0.98, 0);
        arm.castShadow = true;
        group.add(arm);

        // Glowing Cupholder Ring
        const ring = new THREE.Mesh(
            new THREE.TorusGeometry(0.09, 0.02, 6, 16),
            is_booked ? materials.blackPlastic : materials.neonStripCyan
        );
        ring.rotation.x = Math.PI / 2;
        ring.position.set(armX, 1.17, -0.22);
        group.add(ring);
    }

    // Heavy Metal Pedestal Base
    const pedestal = new THREE.Mesh(
        new THREE.CylinderGeometry(0.06, 0.08, 0.48, 10),
        materials.metalChrome
    );
    pedestal.position.set(0, 0.25, 0.05);
    pedestal.castShadow = true;
    group.add(pedestal);

    // If booked, add subtle red sold-out indicator marker
    if (is_booked) {
        const soldPin = new THREE.Mesh(
            new THREE.SphereGeometry(0.07, 8, 8),
            new THREE.MeshBasicMaterial({ color: 0xef4444 })
        );
        soldPin.position.set(0, 1.8, 0.5);
        group.add(soldPin);
    }

    // Position seat from Django database coordinates
    group.position.set(x, y, z);

    // Attach metadata for raycasting & selection
    group.userData = {
        seatId: id,
        row,
        number,
        label: `${row}${number}`,
        category,
        price,
        is_booked,
        cushionMesh: cushion,
        backrestMesh: backrest,
        headrestMesh: headrest,
        defaultMaterial: baseMat
    };

    group.traverse((obj) => {
        if (obj.isMesh) {
            obj.userData.parentSeat = group;
        }
    });

    scene.add(group);
    seatMeshMap.set(id, group);

    if (!is_booked) {
        selectableSeats.push(group);
    }

    return group;
}

// ==========================================
// 8. DATA FETCHING FROM DJANGO DRF API
// ==========================================
async function loadShowtimeSeats() {
    try {
        const res = await fetch(`/api/showtimes/${currentShowtimeId}/seats/`);
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

        showtimeData = await res.json();
        const seats = showtimeData.seats || [];

        // Clear existing seats
        selectableSeats.forEach(g => scene.remove(g));
        selectableSeats = [];
        seatMeshMap.clear();

        // Build each seat mesh
        seats.forEach(seat => {
            createSeatMesh(seat);
        });

        // Update HUD seat counts
        updateHUDCounts();

        console.log(`Loaded ${seats.length} 3D seats for showtime ${currentShowtimeId}`);
    } catch (err) {
        console.error('Failed to load 3D seats:', err);
    }
}

// ==========================================
// 9. SEAT SELECTION & HIGHLIGHTING
// ==========================================
export function toggleSeatSelection(group) {
    if (!group || group.userData.is_booked) return;

    const data = group.userData;
    const seatId = data.seatId;

    if (selectedSeats.has(seatId)) {
        // Deselect
        selectedSeats.delete(seatId);
        applySeatMaterial(group, data.defaultMaterial);
    } else {
        // Select
        selectedSeats.set(seatId, {
            id: seatId,
            label: data.label,
            category: data.category,
            price: data.price,
            row: data.row,
            number: data.number,
            group
        });
        applySeatMaterial(group, materials.seatSelected);
    }

    // Refresh overlay UI & totals
    updateOrderSummaryUI();
    renderSelectedChips();
}

function applySeatMaterial(group, material) {
    if (!group.userData) return;
    const { cushionMesh, backrestMesh, headrestMesh } = group.userData;
    if (cushionMesh) cushionMesh.material = material;
    if (backrestMesh) backrestMesh.material = material;
    if (headrestMesh) headrestMesh.material = material;
}

// Quick-Pick seat quantity selector
window.quickPickSeats = function(count) {
    // Clear currently selected
    for (const [id, s] of selectedSeats) {
        applySeatMaterial(s.group, s.group.userData.defaultMaterial);
    }
    selectedSeats.clear();

    // Group available seats by row
    const availableByRow = {};
    selectableSeats.forEach(group => {
        const row = group.userData.row;
        if (!availableByRow[row]) availableByRow[row] = [];
        availableByRow[row].push(group);
    });

    // Try finding consecutive seats starting from highest tier (Row F, E, D, C, B, A)
    const rowOrder = ['F', 'E', 'D', 'C', 'B', 'A'];
    let chosen = [];

    for (const row of rowOrder) {
        const rowSeats = availableByRow[row] || [];
        rowSeats.sort((a, b) => a.userData.number - b.userData.number);

        // Find consecutive slice
        for (let i = 0; i <= rowSeats.length - count; i++) {
            let isConsecutive = true;
            for (let j = 0; j < count - 1; j++) {
                if (rowSeats[i + j + 1].userData.number !== rowSeats[i + j].userData.number + 1) {
                    isConsecutive = false;
                    break;
                }
            }
            if (isConsecutive) {
                chosen = rowSeats.slice(i, i + count);
                break;
            }
        }
        if (chosen.length === count) break;
    }

    // Fallback: pick any top available seats if consecutive not found in single row
    if (chosen.length < count) {
        chosen = selectableSeats.slice(0, count);
    }

    // Select chosen seats
    chosen.forEach(group => toggleSeatSelection(group));

    // Focus camera smoothly towards chosen seats
    if (chosen.length > 0) {
        focusCameraOnSeat(chosen[Math.floor(chosen.length / 2)]);
    }
};

window.clearAllSelectedSeats = function() {
    for (const [id, s] of selectedSeats) {
        applySeatMaterial(s.group, s.group.userData.defaultMaterial);
    }
    selectedSeats.clear();
    updateOrderSummaryUI();
    renderSelectedChips();
};

window.removeSeatById = function(seatId) {
    const item = selectedSeats.get(seatId);
    if (item && item.group) {
        toggleSeatSelection(item.group);
    }
};

// ==========================================
// 10. RAYCASTING & MOUSE INTERACTIONS
// ==========================================
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let hoveredSeat = null;
let pointerDownPos = { x: 0, y: 0 };

renderer.domElement.addEventListener('pointerdown', (e) => {
    pointerDownPos.x = e.clientX;
    pointerDownPos.y = e.clientY;
});

renderer.domElement.addEventListener('pointermove', (e) => {
    const rect = renderer.domElement.getBoundingClientRect();
    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(selectableSeats, true);

    if (intersects.length > 0) {
        const hitGroup = intersects[0].object.userData.parentSeat;
        if (hitGroup && !hitGroup.userData.is_booked) {
            if (hoveredSeat !== hitGroup) {
                // Restore previous
                if (hoveredSeat && !selectedSeats.has(hoveredSeat.userData.seatId)) {
                    applySeatMaterial(hoveredSeat, hoveredSeat.userData.defaultMaterial);
                }
                hoveredSeat = hitGroup;

                // Highlight hover
                if (!selectedSeats.has(hitGroup.userData.seatId)) {
                    applySeatMaterial(hitGroup, materials.seatHover);
                }
            }

            // Update floating tooltip
            const data = hitGroup.userData;
            tooltip.innerHTML = `
                <div class="flex items-center gap-1.5 font-bold">
                    <span class="text-neon font-display">${data.label}</span>
                    <span class="text-gray-400">•</span>
                    <span class="text-cyber-cyan">${data.category}</span>
                </div>
                <div class="text-[10px] text-gray-300 mt-0.5">₹${data.price} • Click to Select</div>
            `;
            tooltip.style.left = `${e.clientX - rect.left + 15}px`;
            tooltip.style.top = `${e.clientY - rect.top - 35}px`;
            tooltip.classList.remove('hidden');
            renderer.domElement.style.cursor = 'pointer';
            return;
        }
    }

    // No hit
    if (hoveredSeat && !selectedSeats.has(hoveredSeat.userData.seatId)) {
        applySeatMaterial(hoveredSeat, hoveredSeat.userData.defaultMaterial);
    }
    hoveredSeat = null;
    tooltip.classList.add('hidden');
    renderer.domElement.style.cursor = 'default';
});

renderer.domElement.addEventListener('pointerup', (e) => {
    const dist = Math.hypot(e.clientX - pointerDownPos.x, e.clientY - pointerDownPos.y);
    if (dist > 5) return; // Drag/orbit gesture, not a click

    const rect = renderer.domElement.getBoundingClientRect();
    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(selectableSeats, true);

    if (intersects.length > 0) {
        const hitGroup = intersects[0].object.userData.parentSeat;
        if (hitGroup) {
            toggleSeatSelection(hitGroup);
        }
    }
});

// ==========================================
// 11. CAMERA PRESETS & SMOOTH TRANSITIONS
// ==========================================
export function setCameraPreset(presetName) {
    let targetPos, targetLookAt;

    switch (presetName) {
        case 'overview':
            targetPos = new THREE.Vector3(0, 10, 18);
            targetLookAt = new THREE.Vector3(0, 2.5, -2);
            break;
        case 'screen':
            targetPos = new THREE.Vector3(0, 4.5, 7.5);
            targetLookAt = new THREE.Vector3(0, 5.2, -7.8);
            break;
        case 'balcony':
            targetPos = new THREE.Vector3(0, 5.2, 5.5);
            targetLookAt = new THREE.Vector3(0, 4.5, -6.5);
            break;
        case 'front':
            targetPos = new THREE.Vector3(0, 1.8, -1.5);
            targetLookAt = new THREE.Vector3(0, 5.2, -7.8);
            break;
        default:
            targetPos = new THREE.Vector3(0, 10, 18);
            targetLookAt = new THREE.Vector3(0, 2.5, -2);
    }

    animateCamera(targetPos, targetLookAt, 1000);
}

function focusCameraOnSeat(group) {
    const seatPos = new THREE.Vector3();
    group.getWorldPosition(seatPos);

    const targetPos = new THREE.Vector3(
        seatPos.x * 0.7,
        seatPos.y + 2.8,
        seatPos.z + 4.2
    );
    animateCamera(targetPos, new THREE.Vector3(0, 4.5, -7.5), 800);
}

function animateCamera(endPos, endTarget, duration = 1000) {
    cameraAnimation = {
        startPos: camera.position.clone(),
        endPos,
        startTarget: controls.target.clone(),
        endTarget,
        startTime: performance.now(),
        duration
    };
}

// Expose camera presets to window for HTML buttons
window.setCameraPreset = setCameraPreset;

// ==========================================
// 12. SCREEN AUDIO & FULLSCREEN CONTROLS
// ==========================================
window.toggleAuditoriumAudio = function() {
    isAudioMuted = !isAudioMuted;
    if (videoElement) {
        videoElement.muted = isAudioMuted;
    }
    const icon = document.getElementById('auditoriumAudioIcon');
    const label = document.getElementById('auditoriumAudioLabel');
    if (icon && label) {
        if (isAudioMuted) {
            icon.className = 'fa-solid fa-volume-xmark';
            label.textContent = 'Muted';
        } else {
            icon.className = 'fa-solid fa-volume-high text-neon';
            label.textContent = 'Trailer Audio On';
        }
    }
};

window.toggleFullscreen = function() {
    if (!document.fullscreenElement) {
        container.requestFullscreen().catch(err => console.warn(err));
    } else {
        document.exitFullscreen().catch(err => console.warn(err));
    }
};

// ==========================================
// 13. UI SUMMARY & SYNC HELPERS
// ==========================================
function updateHUDCounts() {
    const totalAvail = showtimeData ? showtimeData.available_seats : 0;
    const availLabel = document.getElementById('hudAvailableCount');
    if (availLabel) availLabel.textContent = `${totalAvail} Available`;
}

function renderSelectedChips() {
    const container = document.getElementById('selectedSeatsChips');
    if (!container) return;

    if (selectedSeats.size === 0) {
        container.innerHTML = '<span class="text-xs text-gray-500 italic">No seats selected yet. Click any 3D seat above or use Quick Pick.</span>';
        return;
    }

    container.innerHTML = Array.from(selectedSeats.values()).map(seat => `
        <div class="px-2.5 py-1 rounded-lg bg-neon/15 border border-neon/50 text-neon text-xs font-mono font-bold flex items-center gap-1.5 shadow-[0_0_10px_rgba(204,255,0,0.2)] animate-fadeIn">
            <span>${seat.label}</span>
            <span class="text-[9px] text-gray-300 font-normal">₹${seat.price}</span>
            <button type="button" onclick="removeSeatById(${seat.id})" class="text-gray-400 hover:text-white ml-1">✕</button>
        </div>
    `).join('');
}

export function updateOrderSummaryUI() {
    const seatsList = Array.from(selectedSeats.values());
    const snacksList = Array.from(addedSnacks.values());

    const seatsSubtotal = seatsList.reduce((sum, s) => sum + Number(s.price), 0);
    const snacksSubtotal = snacksList.reduce((sum, s) => sum + (Number(s.price) * s.quantity), 0);
    const convenienceFee = seatsList.length > 0 ? 45.00 : 0.00;
    const taxAmount = Math.round(convenienceFee * 0.18 * 100) / 100;
    const grandTotal = Math.round((seatsSubtotal + snacksSubtotal + convenienceFee + taxAmount) * 100) / 100;

    // Update Bottom Bar CTA
    const ctaBtn = document.getElementById('continueToFnBBtn');
    const ctaTotal = document.getElementById('ctaTotalAmount');
    const ctaCount = document.getElementById('ctaSeatCount');

    if (ctaTotal) ctaTotal.textContent = `₹${grandTotal.toFixed(0)}`;
    if (ctaCount) ctaCount.textContent = `${seatsList.length} Seat${seatsList.length === 1 ? '' : 's'}`;
    if (ctaBtn) {
        ctaBtn.disabled = seatsList.length === 0;
        if (seatsList.length > 0) {
            ctaBtn.classList.remove('opacity-50', 'pointer-events-none');
            ctaBtn.classList.add('shadow-neon');
        } else {
            ctaBtn.classList.add('opacity-50', 'pointer-events-none');
            ctaBtn.classList.remove('shadow-neon');
        }
    }

    // Update Persistent Sidebar (Your Order)
    const sidebarSeats = document.getElementById('sidebarSeatsBreakdown');
    if (sidebarSeats) {
        if (seatsList.length === 0) {
            sidebarSeats.innerHTML = '<p class="text-xs text-gray-500 italic">No seats selected.</p>';
        } else {
            sidebarSeats.innerHTML = seatsList.map(s => `
                <div class="flex items-center justify-between text-xs py-1">
                    <span class="text-gray-200"><span class="text-neon font-bold">${s.label}</span> (${s.category})</span>
                    <span class="font-mono text-white">₹${s.price}</span>
                </div>
            `).join('');
        }
    }

    const sidebarSnacks = document.getElementById('sidebarSnacksBreakdown');
    if (sidebarSnacks) {
        if (snacksList.length === 0) {
            sidebarSnacks.innerHTML = '<p class="text-xs text-gray-500 italic">No snacks added.</p>';
        } else {
            sidebarSnacks.innerHTML = snacksList.map(sn => `
                <div class="flex items-center justify-between text-xs py-1">
                    <span class="text-gray-200">${sn.name} <span class="text-gray-400">x${sn.quantity}</span></span>
                    <span class="font-mono text-neon font-bold">₹${(sn.price * sn.quantity).toFixed(0)}</span>
                </div>
            `).join('');
        }
    }

    // Totals in sidebar & checkout
    const setText = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = `₹${val.toFixed(2)}`;
    };

    setText('orderSeatsSubtotal', seatsSubtotal);
    setText('orderSnacksSubtotal', snacksSubtotal);
    setText('orderConvenienceFee', convenienceFee);
    setText('orderTaxAmount', taxAmount);
    setText('orderGrandTotal', grandTotal);
    setText('checkoutModalTotal', grandTotal);
}

// ==========================================
// 14. ANIMATION & RENDER LOOP
// ==========================================
const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);

    const delta = clock.getDelta();
    const time = clock.getElapsedTime();

    // Pulse screen ambient light gently
    if (screenLight) {
        screenLight.intensity = 42 + Math.sin(time * 3) * 6;
    }

    // Smooth Camera Transition Lerp
    if (cameraAnimation) {
        const a = cameraAnimation;
        const elapsed = performance.now() - a.startTime;
        const progress = Math.min(elapsed / a.duration, 1.0);
        const ease = progress * progress * (3.0 - 2.0 * progress); // smoothstep

        camera.position.lerpVectors(a.startPos, a.endPos, ease);
        controls.target.lerpVectors(a.startTarget, a.endTarget, ease);

        if (progress >= 1.0) {
            cameraAnimation = null;
        }
    }

    controls.update();
    renderer.render(scene, camera);
}

// Window Resize Handler
window.addEventListener('resize', () => {
    const width = container.clientWidth;
    const height = container.clientHeight;
    if (!width || !height) return;

    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
});

// Initialize
buildAuditoriumRoom();
setupCinemaScreen(currentVideoMp4, currentMovieTitle);
loadShowtimeSeats();
animate();
updateOrderSummaryUI();
renderSelectedChips();
