# ==============================================
# BOT BACKEND - RECEIVES FILTERS FROM CLIENT
# ==============================================
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time

app = Flask(__name__)
CORS(app)

# ==============================================
# API ENDPOINT: Validate a task with client's filters
# ==============================================
@app.route('/validate', methods=['POST'])
def validate_task():
    """
    Receives task data AND the client's filters.
    Runs the comparison and returns "claim" or "skip".
    """
    try:
        data = request.get_json()
        
        # Extract task data
        task = data.get('task', {})
        unit_id = task.get('unitId', '')
        pay = float(task.get('pay', 0))
        length = float(task.get('length', 0))
        unclaimed = int(task.get('unclaimed', 0))
        speakers = int(task.get('speakers', 0))
        format_str = task.get('format', '')
        
        # Extract client's filters
        filters = data.get('filters', {})
        
        print(f"🔍 Validating: {unit_id}")
        print(f"   Client filters: {filters}")
        
        # ==========================================
        # RUN FILTERS (Using client's values)
        # ==========================================
        
        # 1. Blacklist (client's own blacklist)
        blacklist = filters.get('blacklist', [])
        for word in blacklist:
            if word.lower() in unit_id.lower():
                return jsonify({
                    'valid': False,
                    'reason': f'Blacklisted word: "{word}"'
                })
        
        # 2. Pay filters (client's own range)
        min_pay = filters.get('minPay', 0)
        max_pay = filters.get('maxPay', 999999)
        if pay < min_pay or pay > max_pay:
            return jsonify({
                'valid': False,
                'reason': f'Pay ${pay} outside range (${min_pay}-${max_pay})'
            })
        
        # 3. Length filters (client's own range)
        min_length = filters.get('minLength', 0)
        max_length = filters.get('maxLength', 999999)
        if length < min_length or length > max_length:
            return jsonify({
                'valid': False,
                'reason': f'Length {length}min outside range ({min_length}-{max_length})'
            })
        
        # 4. Unclaimed filters (client's own range)
        min_unclaimed = filters.get('minUnclaimed', 0)
        max_unclaimed = filters.get('maxUnclaimed', 999999)
        if unclaimed < min_unclaimed or unclaimed > max_unclaimed:
            return jsonify({
                'valid': False,
                'reason': f'Unclaimed {unclaimed} outside range ({min_unclaimed}-{max_unclaimed})'
            })
        
        # 5. Speaker filters (client's own range)
        ignore_speakers = filters.get('ignoreSpeakers', False)
        if not ignore_speakers:
            min_speakers = filters.get('minSpeakers', 0)
            max_speakers = filters.get('maxSpeakers', 999999)
            if speakers < min_speakers or speakers > max_speakers:
                return jsonify({
                    'valid': False,
                    'reason': f'Speakers {speakers} outside range ({min_speakers}-{max_speakers})'
                })
        
        # 6. Format filters (client's own allowed formats)
        allowed_formats = filters.get('formats', [])
        if allowed_formats and format_str not in allowed_formats:
            return jsonify({
                'valid': False,
                'reason': f'Format "{format_str}" not allowed'
            })
        
        # ==========================================
        # ALL FILTERS PASSED → CLAIM IT!
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
# HEALTH CHECK
# ==============================================
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'OK',
        'message': 'Bot backend is running!'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
