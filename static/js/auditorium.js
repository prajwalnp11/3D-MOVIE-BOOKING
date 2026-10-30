
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/controls/OrbitControls.js';

const container = document.getElementById('theatre3D');

const movieSelect = document.getElementById('movieSelect');
const showtimeSelect = document.getElementById('showtimeSelect');
const selectedSeatsElement = document.getElementById('selectedSeats');
const totalAmountElement = document.getElementById('totalAmount');
const continueButton = document.getElementById('continueBooking');

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x100c0c);
scene.fog = new THREE.Fog(0x100c0c, 20, 38);

const camera = new THREE.PerspectiveCamera(
    50,
    container.clientWidth / container.clientHeight,
    0.1,
    100
);

camera.position.set(0, 8, 16);

const renderer = new THREE.WebGLRenderer({
    antialias: true
});

renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(container.clientWidth, container.clientHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

container.innerHTML = '';
container.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 1.5, 0);
controls.enableDamping = true;
controls.minDistance = 9;
controls.maxDistance = 23;
controls.maxPolarAngle = Math.PI / 2.05;
controls.minPolarAngle = 0.25;


// Lighting

scene.add(new THREE.AmbientLight(0xffffff, 1.4));

const mainLight = new THREE.DirectionalLight(0xffffff, 2.5);
mainLight.position.set(0, 12, 5);
mainLight.castShadow = true;
scene.add(mainLight);

const screenLight = new THREE.PointLight(0x6688ff, 35, 18);
screenLight.position.set(0, 5, -6);
scene.add(screenLight);


// Materials

const floorMaterial = new THREE.MeshStandardMaterial({
    color: 0x242020,
    roughness: 0.9
});

const redMaterial = new THREE.MeshStandardMaterial({
    color: 0x9e1717,
    roughness: 0.75
});

const goldMaterial = new THREE.MeshStandardMaterial({
    color: 0xd6a84f,
    roughness: 0.5
});

const darkMaterial = new THREE.MeshStandardMaterial({
    color: 0x151515
});


// Theatre floor

const floor = new THREE.Mesh(
    new THREE.BoxGeometry(16, 0.3, 16),
    floorMaterial
);

floor.position.set(0, -0.2, 0);
floor.receiveShadow = true;
scene.add(floor);


// Theatre walls

function createWall(width, height, depth, x, y, z) {
    const wall = new THREE.Mesh(
        new THREE.BoxGeometry(width, height, depth),
        new THREE.MeshStandardMaterial({
            color: 0x302020,
            roughness: 0.9
        })
    );

    wall.position.set(x, y, z);
    scene.add(wall);
}

createWall(16, 7, 0.3, 0, 3.3, -7.8);
createWall(0.3, 7, 16, -8, 3.3, 0);
createWall(0.3, 7, 16, 8, 3.3, 0);


// Cinema screen

const screenFrame = new THREE.Mesh(
    new THREE.BoxGeometry(9, 4.5, 0.3),
    goldMaterial
);

screenFrame.position.set(0, 4.1, -7.45);
scene.add(screenFrame);

const screen = new THREE.Mesh(
    new THREE.PlaneGeometry(8.65, 4.15),
    new THREE.MeshBasicMaterial({
        color: 0x101a32
    })
);

screen.position.set(0, 4.1, -7.25);
scene.add(screen);


// Screen graphic

const screenCanvas = document.createElement('canvas');
screenCanvas.width = 1024;
screenCanvas.height = 512;

const ctx = screenCanvas.getContext('2d');

function drawScreen(title = 'CINEVERSE') {
    const gradient = ctx.createLinearGradient(0, 0, 1024, 512);
    gradient.addColorStop(0, '#101b35');
    gradient.addColorStop(1, '#391616');

    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 1024, 512);

    ctx.fillStyle = '#d6a84f';
    ctx.font = 'bold 65px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('CINEVERSE', 512, 205);

    ctx.fillStyle = '#ffffff';
    ctx.font = '34px Arial';
    ctx.fillText(title.substring(0, 35), 512, 280);

    ctx.font = '24px Arial';
    ctx.fillStyle = '#cccccc';
    ctx.fillText('YOUR CINEMA EXPERIENCE STARTS HERE', 512, 350);
}

drawScreen();

const screenTexture = new THREE.CanvasTexture(screenCanvas);
screen.material = new THREE.MeshBasicMaterial({
    map: screenTexture
});

movieSelect.addEventListener('change', () => {
    const selectedOption = movieSelect.options[movieSelect.selectedIndex];
    const movieTitle = selectedOption.text || 'Choose a movie';

    drawScreen(movieTitle);
    screenTexture.needsUpdate = true;
});


// Stage

const stage = new THREE.Mesh(
    new THREE.BoxGeometry(11, 0.5, 1.4),
    darkMaterial
);

stage.position.set(0, 0.1, -6.2);
scene.add(stage);


// Seat creation

const selectableSeats = [];
const selectedSeats = new Map();

const seatPrices = {
    NORMAL: 150,
    PREMIUM: 250,
    RECLINER: 400
};

const seatMaterials = {
    NORMAL: redMaterial,
    PREMIUM: new THREE.MeshStandardMaterial({ color: 0x9b5720 }),
    RECLINER: new THREE.MeshStandardMaterial({ color: 0x363b75 })
};

const seatRows = ['A', 'B', 'C', 'D', 'E', 'F'];

function createSeat(row, number, category, x, z) {
    const group = new THREE.Group();

    const cushion = new THREE.Mesh(
        new THREE.BoxGeometry(0.75, 0.22, 0.72),
        seatMaterials[category]
    );

    cushion.position.set(0, 0.65, 0.05);
    cushion.castShadow = true;
    group.add(cushion);

    const backrest = new THREE.Mesh(
        new THREE.BoxGeometry(0.75, 0.9, 0.2),
        seatMaterials[category]
    );

    backrest.position.set(0, 1.15, -0.28);
    backrest.castShadow = true;
    group.add(backrest);

    const armMaterial = new THREE.MeshStandardMaterial({
        color: 0x282828,
        metalness: 0.3
    });

    [-0.42, 0.42].forEach(side => {
        const arm = new THREE.Mesh(
            new THREE.BoxGeometry(0.12, 0.38, 0.75),
            armMaterial
        );

        arm.position.set(side, 0.82, 0.05);
        group.add(arm);
    });

    group.position.set(x, 0, z);

    group.userData = {
        row,
        number,
        category,
        price: seatPrices[category],
        unavailable: false
    };

    group.traverse(child => {
        if (child.isMesh) {
            child.userData.seatGroup = group;
        }
    });

    scene.add(group);
    selectableSeats.push(group);
}


// Generate 60 seats

seatRows.forEach((row, rowIndex) => {
    let category = 'NORMAL';

    if (row === 'E') category = 'PREMIUM';
    if (row === 'F') category = 'RECLINER';

    for (let number = 1; number <= 10; number++) {
        const x = (number - 5.5) * 1.1;
        const z = -2.5 + rowIndex * 1.35;

        createSeat(row, number, category, x, z);
    }
});


// Aisle lighting

for (let i = 0; i < 6; i++) {
    const light = new THREE.PointLight(0xd6a84f, 2, 4);
    light.position.set(-6.5, 0.5, -2.5 + i * 1.35);
    scene.add(light);
}


// Mouse interaction

const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

renderer.domElement.addEventListener('pointerdown', event => {
    const rect = renderer.domElement.getBoundingClientRect();

    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);

    const intersects = raycaster.intersectObjects(
        selectableSeats.flatMap(seat => seat.children),
        false
    );

    if (!intersects.length) return;

    const seat = intersects[0].object.userData.seatGroup;

    if (seat) toggleSeat(seat);
});


// Update seat colour

function updateSeatColour(seat, color) {
    seat.traverse(child => {
        if (child.isMesh && child.geometry.type !== 'BoxGeometry') return;

        if (
            child.isMesh &&
            child.material !== undefined &&
            child.material.color
        ) {
            if (child.material !== seat.userData.originalMaterial) {
                // Seat body colour is updated below.
            }
        }
    });

    const category = seat.userData.category;
    const material = selectedSeats.has(seat)
        ? goldMaterial
        : seatMaterials[category];

    seat.children[0].material = material;
    seat.children[1].material = material;
}


// Select or unselect seats

function toggleSeat(seat) {
    if (selectedSeats.has(seat)) {
        selectedSeats.delete(seat);
    } else {
        selectedSeats.set(seat, seat.userData.price);
    }

    updateSeatColour(seat);
    updateSummary();
}


// Booking summary

function updateSummary() {
    const seatNames = [];
    let total = 0;

    selectedSeats.forEach((price, seat) => {
        seatNames.push(
            `${seat.userData.row}${seat.userData.number}`
        );

        total += price;
    });

    selectedSeatsElement.textContent =
        seatNames.length > 0
            ? seatNames.join(', ')
            : 'No seats selected';

    totalAmountElement.textContent =
        `₹${total.toLocaleString('en-IN')}`;

    continueButton.disabled = seatNames.length === 0;
}


// Continue button (demo only)

continueButton.addEventListener('click', () => {
    const movie = movieSelect.options[movieSelect.selectedIndex].text;
    const showtime = showtimeSelect.options[showtimeSelect.selectedIndex].text;

    if (!movieSelect.value || !showtimeSelect.value) {
        alert('Please select a movie and showtime first.');
        return;
    }

    alert(
        `Demo selection\nMovie: ${movie}\nShowtime: ${showtime}\nSeats: ${selectedSeatsElement.textContent}\nTotal: ${totalAmountElement.textContent}\n\nActual booking will be connected in a later step.`
    );
});


// Filter showtimes by movie

movieSelect.addEventListener('change', () => {
    const movieId = movieSelect.value;

    showtimeSelect.value = '';

    Array.from(showtimeSelect.options).forEach(option => {
        if (!option.value) {
            option.hidden = false;
            return;
        }

        option.hidden = option.dataset.movieId !== movieId;
    });
});


// Responsive resizing

window.addEventListener('resize', () => {
    const width = container.clientWidth;
    const height = container.clientHeight;

    camera.aspect = width / height;
    camera.updateProjectionMatrix();

    renderer.setSize(width, height);
});


// Animation

function animate() {
    requestAnimationFrame(animate);

    controls.update();
    renderer.render(scene, camera);
}

animate();

