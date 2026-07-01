# ==============================================
# BOT BACKEND - SECRET LOGIC (Hidden on Render)
# ==============================================
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time

app = Flask(__name__)
CORS(app)  # Allows your extension to talk to this server

# ==============================================
# YOUR SECRET LOGIC (100% HIDDEN FROM USERS)
# ==============================================

# 1. BLACKLIST - Words to block (you can edit this anytime!)
BLACKLIST = [
    "test",
    "sample", 
    "draft",
    "training",
    "demo"
]

# 2. PAY FILTERS ($)
MIN_PAY = 0.1   # Minimum pay per minute
MAX_PAY = 1.0   # Maximum pay per minute

# 3. LENGTH FILTERS (minutes)
MIN_LENGTH = 0   # Minimum audio length
MAX_LENGTH = 60  # Maximum audio length

# 4. UNCLAIMED FILTERS
MIN_UNCLAIMED = 0   # Minimum unclaimed count
MAX_UNCLAIMED = 10  # Maximum unclaimed count

# 5. SPEAKER FILTERS
MIN_SPEAKERS = 0   # Minimum speaker count
MAX_SPEAKERS = 10  # Maximum speaker count

# 6. FORMAT FILTERS
ALLOWED_FORMATS = [
    "Identification by Video",
    "Identification by Audio",
    "Blank"
]

# 7. ACTIVE USERS (Subscription management)
# Add your queue_id here to give yourself access!
ACTIVE_USERS = [
    "1234567890abcdef12345678",  # ← REPLACE THIS with your actual queue_id!
]

# ==============================================
# API ENDPOINT 1: Validate a task
# ==============================================
@app.route('/validate', methods=['POST'])
def validate_task():
    """
    This is the MOST IMPORTANT function.
    It receives a task from the client and decides:
    - YES → claim it
    - NO → skip it
    """
    try:
        # Step 1: Get the task data from the client
        data = request.get_json()
        
        # Step 2: Extract all the task details
        unit_id = data.get('unitId', '')
        pay = float(data.get('pay', 0))
        length = float(data.get('length', 0))
        unclaimed = int(data.get('unclaimed', 0))
        speakers = int(data.get('speakers', 0))
        format_str = data.get('format', '')
        
        print(f"🔍 Validating: {unit_id}")
        print(f"   Pay: ${pay}, Length: {length}min, Unclaimed: {unclaimed}")
        
        # ==========================================
        # STEP 3: RUN ALL FILTERS (SECRET LOGIC)
        # ==========================================
        
        # Filter 1: Blacklist check
        for word in BLACKLIST:
            if word.lower() in unit_id.lower():
                return jsonify({
                    'valid': False,
                    'reason': f'Blacklisted word: "{word}"'
                })
        
        # Filter 2: Pay check
        if pay < MIN_PAY or pay > MAX_PAY:
            return jsonify({
                'valid': False,
                'reason': f'Pay ${pay} outside range (${MIN_PAY}-${MAX_PAY})'
            })
        
        # Filter 3: Length check
        if length < MIN_LENGTH or length > MAX_LENGTH:
            return jsonify({
                'valid': False,
                'reason': f'Length {length}min outside range ({MIN_LENGTH}-{MAX_LENGTH})'
            })
        
        # Filter 4: Unclaimed check
        if unclaimed < MIN_UNCLAIMED or unclaimed > MAX_UNCLAIMED:
            return jsonify({
                'valid': False,
                'reason': f'Unclaimed {unclaimed} outside range ({MIN_UNCLAIMED}-{MAX_UNCLAIMED})'
            })
        
        # Filter 5: Speaker check
        if speakers < MIN_SPEAKERS or speakers > MAX_SPEAKERS:
            return jsonify({
                'valid': False,
                'reason': f'Speakers {speakers} outside range ({MIN_SPEAKERS}-{MAX_SPEAKERS})'
            })
        
        # Filter 6: Format check
        if format_str and format_str not in ALLOWED_FORMATS:
            return jsonify({
                'valid': False,
                'reason': f'Format "{format_str}" not allowed'
            })
        
        # ==========================================
        # STEP 4: ALL FILTERS PASSED → CLAIM IT!
        # ==========================================
        print(f"✅ {unit_id} PASSED all filters!")
        return jsonify({
            'valid': True,
            'reason': 'All filters passed ✅'
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({
            'valid': False,
            'reason': f'Server error: {str(e)}'
        }), 500

# ==============================================
# API ENDPOINT 2: Check subscription
# ==============================================
@app.route('/check', methods=['GET'])
def check_subscription():
    """
    This checks if a user has an active subscription.
    """
    queue_id = request.args.get('queue_id', '')
    
    if queue_id in ACTIVE_USERS:
        return jsonify({
            'valid': True,
            'timestamp': int(time.time() * 1000),
            'signature': 'your_hmac_signature_here'
        })
    else:
        return jsonify({
            'valid': False,
            'timestamp': int(time.time() * 1000),
            'signature': 'your_hmac_signature_here'
        })

# ==============================================
# HEALTH CHECK (Render needs this)
# ==============================================
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'OK',
        'message': 'Bot backend is running!'
    })

# ==============================================
# START THE SERVER
# ==============================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)