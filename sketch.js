var canvas, gridSize, padding;
var ampSlider; // Slider for amplification

function setup() {
    canvas = createCanvas(windowWidth, windowHeight);
    gridSize = min(width, height) / 4; // Grid cell size (4x4 grid)
    padding = gridSize * 0.1; // Padding around each cell
    
    // Create slider (1 to 10)
    ampSlider = createSlider(1, 10, 5); // Default value is 5
    ampSlider.position(1500, 20); // Position the slider
    ampSlider.style('width', '150px'); // Set slider width
}

function draw() {
    background(255); // Clear canvas
    noStroke();
    
    var amplification = ampSlider.value(); // Get amplification factor

    // Read touch data from Bela
    var touchData = Bela.data.buffers[0]; // Data sent on channel 0
    if (!touchData || touchData.length < 8) return; // Skip if no data or insufficient channels
    
    var gridData = [];
    
    // Loop through the individual lanes and calculate all possible grid points
    for (var i = 7; i >= 4; i--) {
    	for (var j = 3; j >= 0; j--) {
    		gridData.push((touchData[i]+touchData[j])*amplification);
    	}
    }

    // Loop through 4x4 grid
    for (var row = 0; row < 4; row++) {
        for (var col = 0; col < 4; col++) {
        	
            var index = row * 4 + col; // Map grid to linear index
            if (index < gridData.length) {
                var value = gridData[index]*5; // Get touch value
                var cellX = col * gridSize; // X position
                var cellY = row * gridSize; // Y position

                // Map touch value to color intensity (blue shade)
                var intensity = map(value, 0, 5, 0, 255); // Scale 0-1 to 0-255
                var intensityR = map(value, 0, 1, 0, 255); // Scale 0-1 to 0-255
                var intensityG = map(value, 0, 15, 0, 255); // Scale 0-1 to 0-255
                fill(intensityR, intensityG, intensity); // Blue shade based on touch value
                rect(cellX + padding, cellY + padding, gridSize - 2 * padding, gridSize - 2 * padding);

                // Add value as text inside the cell for debugging
                fill(255);
                textAlign(CENTER, CENTER);
                text(value.toFixed(2), cellX + gridSize / 2, cellY + gridSize / 2);
            }
        }
    }
    
    gridData = [];
}
