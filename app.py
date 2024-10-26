from flask import Flask, render_template_string, request, jsonify
import os
from dna_storage import DNAStorageSystem, ErrorCorrection

app = Flask(__name__)

# Initialize the storage system
storage_system = DNAStorageSystem()
error_correction = ErrorCorrection()

# HTML template as a string with animation
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>DNA Storage Interface</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .animation-container {
            margin: 20px 0;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 4px;
            min-height: 200px;
        }
        .dna-position {
            display: inline-block;
            margin: 5px;
            padding: 10px;
            background-color: #e9ecef;
            border-radius: 4px;
            position: relative;
            transition: all 0.5s ease;
            opacity: 0;
        }
        .dna-position.visible {
            opacity: 1;
        }
        .methyl-group {
            position: absolute;
            top: -10px;
            right: -5px;
            color: red;
            font-size: 20px;
            opacity: 0;
            transition: opacity 0.5s ease;
        }
        .methyl-group.visible {
            opacity: 1;
        }
        .binary-bit {
            display: inline-block;
            margin: 5px;
            padding: 10px;
            background-color: #e9ecef;
            border-radius: 4px;
            transition: all 0.5s ease;
        }
        .conversion-arrow {
            display: block;
            text-align: center;
            font-size: 24px;
            margin: 10px 0;
            color: #007bff;
        }
        .btn {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .btn:hover {
            background-color: #0056b3;
        }
        .step-display {
            margin: 10px 0;
            font-weight: bold;
            color: #007bff;
        }
        .result {
            margin-top: 20px;
            padding: 10px;
            background-color: #e9ecef;
            border-radius: 4px;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .animate-in {
            animation: fadeIn 0.5s ease forwards;
        }
        
        /* New styles for density visualization */
        .density-container {
            margin: 20px 0;
            padding: 20px;
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .storage-layer {
            margin: 15px 0;
            padding: 10px;
            border: 1px solid #dee2e6;
            border-radius: 4px;
        }
        
        .layer-title {
            font-weight: bold;
            margin-bottom: 10px;
            color: #0056b3;
        }
        
        .density-bit {
            display: inline-block;
            width: 30px;
            height: 30px;
            margin: 2px;
            line-height: 30px;
            text-align: center;
            border-radius: 4px;
            font-family: monospace;
            transition: all 0.3s ease;
        }
        
        .base-bit {
            background-color: #e9ecef;
        }
        
        .methyl-bit {
            background-color: #f8d7da;
        }
        
        .combined-container {
            position: relative;
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 4px;
        }
        
        .density-explanation {
            margin: 10px 0;
            padding: 10px;
            background-color: #e7f5ff;
            border-radius: 4px;
            font-size: 0.9em;
        }
        
        .density-stats {
            margin-top: 15px;
            padding: 10px;
            background-color: #d4edda;
            border-radius: 4px;
        }
        
        .arrow-connector {
            text-align: center;
            color: #6c757d;
            margin: 10px 0;
        }
        /* New styles for enzyme animation */
        .enzyme {
            width: 40px;
            height: 40px;
            background-color: #007bff;
            border-radius: 50%;
            position: absolute;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
            transition: all 0.5s ease;
            cursor: pointer;
            z-index: 100;
        }
        
        .methyl-group {
            position: absolute;
            top: -10px;
            right: -5px;
            color: red;
            font-size: 20px;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .dna-sequence {
            position: relative;
            min-height: 100px;
            margin: 40px 0;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 8px;
        }
        
        .dna-position {
            display: inline-block;
            margin: 5px;
            padding: 15px;
            background-color: #e9ecef;
            border-radius: 4px;
            position: relative;
            font-size: 18px;
            font-weight: bold;
        }
        
        .enzyme-info {
            margin: 20px 0;
            padding: 15px;
            background-color: #e7f5ff;
            border-radius: 8px;
            font-size: 0.9em;
        }
        
        .step-explanation {
            margin: 10px 0;
            padding: 10px;
            background-color: #fff3cd;
            border-radius: 4px;
            display: none;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        
        .enzyme.active {
            animation: pulse 1s infinite;
        }
        
        .control-panel {
            margin: 20px 0;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>DNA Storage System</h1>
        
        <div class="form-group">
            <h2>Encode Data</h2>
            <form id="encodeForm">
                <input type="text" id="inputData" placeholder="Enter binary data (e.g., 10110010)" 
                       pattern="[01]+" required style="width: 300px; padding: 5px;">
                <button type="submit" class="btn">Encode</button>
            </form>
        </div>

        <div class="animation-container">
            <div class="step-display" id="stepDisplay">Step: Input Data</div>
            <div id="binaryContainer"></div>
            <div class="conversion-arrow">↓</div>
            <div id="errorCorrectionContainer"></div>
            <div class="conversion-arrow">↓</div>
            <div id="dnaContainer"></div>
        </div>
        
        <div class="form-group">
            <h2>Decode Data</h2>
            <button onclick="decodeCurrentSequence()" class="btn">Decode Current Sequence</button>
        </div>

        <div class="result" id="result"></div>
    <div class="density-container">
            <h3>Information Density Visualization</h3>
            
            <div class="storage-layer">
                <div class="layer-title">Layer 1: Base Sequence Storage</div>
                <div id="baseLayer"></div>
                <div class="density-explanation">
                    Each DNA base (A, T, C, G) can store 2 bits of information (2² = 4 possibilities)
                </div>
            </div>
            
            <div class="arrow-connector">+</div>
            
            <div class="storage-layer">
                <div class="layer-title">Layer 2: Methylation State</div>
                <div id="methylLayer"></div>
                <div class="density-explanation">
                    Each position can be methylated (1) or unmethylated (0), adding 1 extra bit per position
                </div>
            </div>
            
            <div class="arrow-connector">↓</div>
            
            <div class="combined-container">
                <div class="layer-title">Combined Storage Density</div>
                <div id="combinedLayer"></div>
                <div class="density-explanation">
                    Total bits per position = 2 (base) + 1 (methylation) = 3 bits
                </div>
            </div>
            
            <div class="density-stats" id="densityStats">
                Loading density statistics...
            </div>
        </div>
    </div>
    </div>

    <script>
        function sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }

        async function animateConversion(originalData, encodedData, dnaSequence) {
            // Clear previous animations
            document.getElementById('binaryContainer').innerHTML = '';
            document.getElementById('errorCorrectionContainer').innerHTML = '';
            document.getElementById('dnaContainer').innerHTML = '';
            
            // Step 1: Show original binary
            document.getElementById('stepDisplay').textContent = 'Step 1: Original Binary Data';
            const binaryContainer = document.getElementById('binaryContainer');
            for (let bit of originalData) {
                const bitElement = document.createElement('div');
                bitElement.className = 'binary-bit';
                bitElement.textContent = bit;
                binaryContainer.appendChild(bitElement);
                await sleep(200);
            }
            
            // Step 2: Show error correction
            await sleep(500);
            document.getElementById('stepDisplay').textContent = 'Step 2: Error Correction (3x Redundancy)';
            const errorContainer = document.getElementById('errorCorrectionContainer');
            for (let bit of encodedData) {
                const bitElement = document.createElement('div');
                bitElement.className = 'binary-bit';
                bitElement.textContent = bit;
                errorContainer.appendChild(bitElement);
                await sleep(100);
            }
            
            // Step 3: Convert to DNA
            await sleep(500);
            document.getElementById('stepDisplay').textContent = 'Step 3: DNA Encoding with Modifications';
            const dnaContainer = document.getElementById('dnaContainer');
            for (let pos of dnaSequence) {
                const posElement = document.createElement('div');
                posElement.className = 'dna-position';
                posElement.innerHTML = `<strong>${pos.base}</strong>`;
                dnaContainer.appendChild(posElement);
                
                await sleep(200);
                posElement.classList.add('visible');
                
                if (pos.modifications.includes('Me')) {
                    const methylGroup = document.createElement('div');
                    methylGroup.className = 'methyl-group';
                    methylGroup.innerHTML = '•';
                    posElement.appendChild(methylGroup);
                    await sleep(200);
                    methylGroup.classList.add('visible');
                }
            }
            
            document.getElementById('stepDisplay').textContent = 'Encoding Complete!';
        }

        document.getElementById('encodeForm').onsubmit = function(e) {
            e.preventDefault();
            const data = document.getElementById('inputData').value;
            
            fetch('/encode', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({data: data}),
            })
            .then(response => response.json())
            .then(data => {
                animateConversion(data.original_data, data.encoded_data, data.dna_sequence);
                document.getElementById('result').innerHTML = 
                    `<strong>Encoded Data:</strong><br>Original: ${data.original_data}<br>` +
                    `With Error Correction: ${data.encoded_data}`;
            });
        };

        async function decodeCurrentSequence() {
            document.getElementById('stepDisplay').textContent = 'Decoding DNA Sequence...';
            
            const response = await fetch('/decode', {
                method: 'GET',
            });
            const data = await response.json();
            
            document.getElementById('result').innerHTML += 
                `<br><strong>Decoded Data:</strong><br>${data.decoded_data}`;
            
            document.getElementById('stepDisplay').textContent = 'Decoding Complete!';
        }
          // Previous script content remains
        
        async function updateDensityVisualization(dnaSequence) {
            const baseLayer = document.getElementById('baseLayer');
            const methylLayer = document.getElementById('methylLayer');
            const combinedLayer = document.getElementById('combinedLayer');
            const statsDiv = document.getElementById('densityStats');
            
            baseLayer.innerHTML = '';
            methylLayer.innerHTML = '';
            combinedLayer.innerHTML = '';
            
            let totalBits = 0;
            
            for (let pos of dnaSequence) {
                // Base layer (2 bits)
                const baseBits = document.createElement('div');
                baseBits.className = 'density-bit base-bit';
                baseBits.textContent = pos.base;
                baseLayer.appendChild(baseBits);
                
                // Methylation layer (1 bit)
                const methylBit = document.createElement('div');
                methylBit.className = 'density-bit methyl-bit';
                methylBit.textContent = pos.modifications.includes('Me') ? '1' : '0';
                methylLayer.appendChild(methylBit);
                
                // Combined visualization
                const combinedBit = document.createElement('div');
                combinedBit.className = 'density-bit';
                combinedBit.style.backgroundColor = pos.modifications.includes('Me') ? '#f8d7da' : '#e9ecef';
                combinedBit.textContent = pos.base;
                combinedLayer.appendChild(combinedBit);
                
                totalBits += 3; // 2 from base + 1 from methylation
                await sleep(100);
            }
            
            // Update density statistics
            statsDiv.innerHTML = `
                <strong>Storage Density Analysis:</strong><br>
                Base Sequence: ${dnaSequence.length * 2} bits<br>
                Methylation Layer: ${dnaSequence.length} bits<br>
                Total Storage: ${totalBits} bits<br>
                Density Increase: +50% from methylation
            `;
        }
        
        // Modify the existing encode form handler
        document.getElementById('encodeForm').onsubmit = function(e) {
            e.preventDefault();
            const data = document.getElementById('inputData').value;
            
            fetch('/encode', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({data: data}),
            })
            .then(response => response.json())
            .then(data => {
                animateConversion(data.original_data, data.encoded_data, data.dna_sequence);
                updateDensityVisualization(data.dna_sequence);
                document.getElementById('result').innerHTML = 
                    `<strong>Encoded Data:</strong><br>Original: ${data.original_data}<br>` +
                    `With Error Correction: ${data.encoded_data}`;
            });
        };
    </script>
</body>
</html>
"""

# Store the current DNA sequence in memory
current_dna_sequence = None


@app.route("/")
def index():
    return render_template_string(TEMPLATE)

@app.route('/health')
def health_check():
    return {'status': 'healthy'}, 200

@app.route("/encode", methods=["POST"])
def encode():
    global current_dna_sequence
    data = request.json.get("data", "")

    # Add error correction
    encoded_data = error_correction.encode(data)

    # Convert to DNA
    current_dna_sequence = storage_system.encode_to_dna(encoded_data)

    # Prepare sequence for visualization
    sequence_viz = []
    for pos in current_dna_sequence:
        mods = []
        if pos.modifications.methylated:
            mods.append("Me")
        if pos.modifications.hydroxymethylated:
            mods.append("hMe")
        if pos.modifications.formylated:
            mods.append("fC")

        sequence_viz.append(
            {"base": pos.base, "modifications": mods, "backbone": pos.backbone}
        )

    return jsonify(
        {
            "original_data": data,
            "encoded_data": encoded_data,
            "dna_sequence": sequence_viz,
        }
    )


@app.route("/decode", methods=["GET"])
def decode():
    global current_dna_sequence
    if current_dna_sequence is None:
        return jsonify({"error": "No DNA sequence to decode"}), 400

    # Decode DNA back to binary
    decoded_data = storage_system.decode_from_dna(current_dna_sequence)
    final_data = error_correction.decode(decoded_data)

    return jsonify({"decoded_data": final_data})


if __name__ == "__main__":
    print("Starting DNA Storage Web Interface...")
    port = os.environ.get('PORT', 8080)
    app.run(host='0.0.0.0', port=port)
