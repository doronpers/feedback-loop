# AI Development Patterns & Feedback Loop

This document describes reusable patterns for AI-assisted development and demonstrates a feedback loop for continuous improvement.

## 🎯 Workflow Philosophy

**Core principle:** AI as a collaborative partner, not just a code generator.

```
┌─────────────────────────────────────────────────────────────────┐
│                    MY DEVELOPMENT LOOP                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   0. ORIENT ──► 1. DEFINE ──► 2. DESIGN ──► 3. BUILD            │
│      │            │             │             │                 │
│      │            │             │             ▼                 │
│      │            │             │         [AI Agent]            │
│      │            │             │             │                 │
│      │            │             │             ▼                 │
│      │            │             │      4. VERIFY ◄──[AI Review] │
│      │            │             │             │                 │
│      │            │             │             ▼                 │
│      │            │             │      4.5 CALIBRATE            │
│      │            │             │             │                 │
│      │            │             │             ▼                 │
│      │            │             │         5. HARDEN             │
│      │            │             │             │                 │
│      │            ▼             ▼             ▼                 │
│      └────────────┴─────────────┴─────────────┘                 │
│                       (Feedback loops to all stages)            │
│                                                                 │
│   Key:  Humans guide, AI assists, both verify at gates          │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Tech Stack Context

- **Backend**: Python 3.x, FastAPI, numpy, audio processing
- **Frontend**: Vite, React/TypeScript
- **Infrastructure**: Docker, nginx, SSL/TLS
- **Deployment**: Render.com / cloud platforms

## Development Stages

### Stage 0: ORIENT 🧭 [System 2 Required]

**Purpose:** Establish mental models and check assumptions before diving into work.

**Key Questions:**
- What mental model am I using for this problem?
- What assumptions am I carrying from previous sessions?
- Is this the right problem to solve right now?
- What constraints are active? (time, resources, compliance)
- What's the success criteria?

**Why This Matters:**
- Prevents solving the wrong problem efficiently
- Surfaces hidden assumptions that cause rework
- Aligns human intuition with AI capabilities
- Reduces context pollution from prior sessions

**Example Orient Checklist:**
```markdown
□ Problem clearly stated (not just symptoms)
□ Constraints identified (performance, compliance, budget)
□ Success criteria defined (measurable)
□ Prior similar solutions reviewed (what worked/failed)
□ Current mental model articulated (can explain to rubber duck)
```

---

### Stage 1: DEFINE 🎯 [System 2 Required]

**Human Gap:** Exploring full possibility space  
**AI Fills:** Generating alternative approaches, researching patterns  
**AI Gap:** Judging relevance to real constraints  
**Human Fills:** Filtering based on domain knowledge and tacit requirements

**Feedback Loop:** Learning propagates back to reframe the problem itself. If implementation reveals wrong assumptions, return to ORIENT/DEFINE, don't force the solution.

---

### Stage 2: DESIGN 🏗️ [System 1 + System 2]

**Human Gap:** Generating pattern variations quickly  
**AI Fills:** Creating multiple design options, architectural patterns  
**AI Gap:** Selecting based on tacit domain knowledge  
**Human Fills:** Choosing design based on maintenance burden, team expertise, real-world constraints

---

### Stage 3: BUILD 🔨 [System 1 Acceptable]

**Human Gap:** Speed, syntax recall, boilerplate  
**AI Fills:** Fast code generation, API usage, common patterns  
**AI Gap:** Physics/compliance correctness, domain edge cases  
**Human Fills:** Validating domain-specific correctness, security implications

---

### Stage 4: VERIFY ✓ [System 2 Required]

**Human Gap:** Finding unknown unknowns, exhaustive test cases  
**AI Fills:** Generating test scenarios, exploring edge cases  
**AI Gap:** Validating against ground truth, real-world data  
**Human Fills:** Confirming behavior matches actual requirements, domain validation

---

### Stage 4.5: CALIBRATE 🎚️ [System 2 Required]

**Purpose:** Explicitly assess confidence and risk before hardening.

For each AI output, rate:
- **Epistemic Confidence:** How certain is the AI about correctness? (Low/Medium/High)
- **Domain Fit:** Does this match known patterns in YOUR codebase? (Poor/Fair/Good)
- **Failure Severity:** What's the worst-case if this is wrong? (Low/Medium/High/Critical)

**Decision Matrix:**

| Confidence | Failure Severity | Action |
|------------|------------------|--------|
| Low | High/Critical | **Human deep review required** |
| Low | Medium | Add extra tests, code review |
| High | Critical | Human verification + ensemble reasoning |
| High | High | Automated verification + spot checks |
| High | Low | Automated verification sufficient |

**Why This Matters:**
- AI outputs trigger System 1 (fast, intuitive acceptance)
- This gate forces System 2 (slow, deliberate verification)
- Prevents overconfidence in AI-generated solutions
- Surfaces areas needing human expertise

---

### Stage 5: HARDEN 🛡️ [System 2 Required]

**Human Gap:** Exhaustive enumeration of edge cases  
**AI Fills:** Security checklist generation, vulnerability scanning  
**AI Gap:** Prioritizing real-world risk severity  
**Human Fills:** Risk assessment based on actual usage patterns and compliance needs

---

## The Feedback Loop Process

```
ORIENT → DEFINE → DESIGN → BUILD → VERIFY → CALIBRATE → HARDEN
   ▲        ▲        ▲        │        │         │         │
   │        │        │        ▼        ▼         ▼         ▼
   │        │        │    [AI Agent] [AI Review] [Human]  [Tools]
   │        │        │        │        │         │         │
   │        └────────┴────────┴────────┴─────────┴─────────┘
   │                                   ↓
   │                            Retrospective
   │                                   ↓
   │                         Update AI_PATTERNS.md
   │                                   ↓
   └──────────────────────   Better prompts next time
```

**Key Insight:** Feedback loops exist at ALL stages, not just BUILD→VERIFY. Learning from VERIFY can reframe DEFINE, and retrospectives improve ORIENT.

## 🎭 Domain-Specific AI Blind Spots

AI assistants lack tacit domain knowledge and consistently make specific mistakes in specialized fields. For audio forensics, physics-based analysis, and financial compliance work:

### Audio Processing Edge Cases

#### ❌ AI Consistently Wrong: Array Dimension Assumptions
```python
# AI often assumes audio shape incorrectly
sample_rate = audio.shape[0] / duration  # WRONG: shape[0] is samples, not rate
```

#### ✅ Explicit Verification
```python
import numpy as np
import logging

logger = logging.getLogger(__name__)

def validate_audio_array(audio: np.ndarray, metadata: dict) -> bool:
    """Validate audio array dimensions and extract sample rate safely."""
    # CRITICAL: Verify dimensions first
    assert audio.ndim in (1, 2), f"Expected mono/stereo, got shape {audio.shape}"
    
    # NEVER derive sample rate from array shape
    sample_rate = metadata.get('sample_rate')
    if sample_rate is None:
        logger.debug("Sample rate missing from metadata")
        return False
    
    # Validate mono (1D) or stereo (2D)
    if audio.ndim == 2:
        channels = audio.shape[1]
        assert channels <= 2, f"Expected max 2 channels, got {channels}"
    
    return True
```

---

### FFT Windowing Assumptions

#### ❌ AI Default: Poor Overlap Settings
```python
# AI often uses insufficient overlap
stft = librosa.stft(audio, hop_length=512)  # Default, not optimal
```

#### ✅ Domain-Appropriate Settings
```python
import librosa
import numpy as np

def compute_stft_forensics(audio: np.ndarray, sr: int = 44100) -> np.ndarray:
    """Compute STFT with forensics-appropriate parameters.
    
    For voice fraud detection, higher overlap reveals microstructure.
    """
    # CRITICAL: 75% overlap for forensic analysis
    n_fft = 2048
    hop_length = n_fft // 4  # 75% overlap, not default 50%
    
    # Hann window reduces spectral leakage
    stft = librosa.stft(
        audio,
        n_fft=n_fft,
        hop_length=hop_length,
        window='hann'
    )
    
    return stft
```

---

### Phase Coherence Calculations

**Critical for EM hum analysis and electrical network frequency (ENF) forensics.**

#### ❌ AI Miss: Phase Wrapping Issues
```python
# AI often forgets phase unwrapping
phase = np.angle(stft)  # Wrapped to [-π, π], discontinuous
```

#### ✅ Proper Phase Coherence
```python
import numpy as np

def compute_phase_coherence(stft: np.ndarray) -> np.ndarray:
    """Compute phase coherence with proper unwrapping.
    
    Essential for EM hum analysis (50/60 Hz) in audio forensics.
    """
    # Extract phase
    phase = np.angle(stft)
    
    # CRITICAL: Unwrap phase to remove 2π discontinuities
    phase_unwrapped = np.unwrap(phase, axis=1)
    
    # Compute instantaneous frequency (phase derivative)
    inst_freq = np.diff(phase_unwrapped, axis=1)
    
    return inst_freq
```

---

### Room Impulse Response Normalization

#### ❌ AI Miss: No Amplitude Normalization
```python
# AI generates RIR without normalization
rir = measure_room_response(signal, recorded)  # Amplitude varies wildly
```

#### ✅ Normalized RIR for Acoustic Analysis
```python
import numpy as np
import logging

logger = logging.getLogger(__name__)

def normalize_rir(rir: np.ndarray, method: str = 'peak') -> np.ndarray:
    """Normalize room impulse response for consistent analysis.
    
    Critical for comparing recordings across different rooms/mics.
    """
    if method == 'peak':
        # Normalize to peak amplitude = 1.0
        peak = np.max(np.abs(rir))
        if peak > 0:
            rir_norm = rir / peak
        else:
            logger.debug("RIR has zero peak, returning original")
            rir_norm = rir
    
    elif method == 'energy':
        # Normalize by energy (RMS)
        energy = np.sqrt(np.mean(rir ** 2))
        if energy > 0:
            rir_norm = rir / energy
        else:
            logger.debug("RIR has zero energy, returning original")
            rir_norm = rir
    
    else:
        raise ValueError(f"Unknown normalization method: {method}")
    
    return rir_norm
```

---

### Compliance-Specific Output Formatting

**Financial Suspicious Activity Report (SAR) requirements.**

#### ❌ AI Miss: Generic Output Format
```python
# AI returns generic dict, not SAR-compliant
return {"suspicious": True, "confidence": 0.87}
```

#### ✅ SAR Narrative Format
```python
from datetime import datetime
from typing import Dict, Any, List

def format_sar_narrative(
    analysis_results: Dict[str, Any],
    audio_metadata: Dict[str, Any],
    threshold_exceeded: List[str]
) -> Dict[str, Any]:
    """Format analysis results as SAR-compliant narrative.
    
    FinCEN requires specific fields and human-readable explanations.
    """
    narrative_parts = []
    
    # CRITICAL: SAR requires "who, what, when, where, why"
    narrative_parts.append(
        f"Voice analysis conducted on {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}. "
    )
    
    # Describe technical findings in plain language
    if 'spectral_anomalies' in threshold_exceeded:
        narrative_parts.append(
            f"Spectral analysis revealed anomalies inconsistent with natural voice production "
            f"(confidence: {analysis_results.get('spectral_confidence', 0):.2%}). "
        )
    
    if 'phase_incoherence' in threshold_exceeded:
        narrative_parts.append(
            f"Phase coherence analysis detected digital manipulation artifacts. "
        )
    
    # CRITICAL: Audit trail - all data sources must be traceable
    sar_output = {
        "sar_narrative": " ".join(narrative_parts),
        "timestamp_utc": datetime.utcnow().isoformat(),
        "analyst_id": audio_metadata.get('analyst_id', 'UNKNOWN'),
        "audio_source": audio_metadata.get('source_file', 'UNKNOWN'),
        "analysis_version": "1.0.0",  # Version tracking required
        "thresholds_exceeded": threshold_exceeded,
        "raw_metrics": analysis_results,  # Preserve for audit
    }
    
    return sar_output
```

**Key SAR Requirements AI Misses:**
- Human-readable narrative (not just scores)
- Audit trail completeness (who, what, when, where)
- Version tracking for analysis algorithms
- Explainability (regulators must understand methodology)
- Data retention metadata (for cross-jurisdictional compliance)

---

## Core Best Practices

### 1. NumPy Types Converted Before JSON Serialization

#### ❌ Bad Pattern
```python
import json
import numpy as np

def process_data_bad(data_array):
    result = {
        "mean": np.mean(data_array),  # NumPy float64
        "std": np.std(data_array),    # NumPy float64
        "max": np.max(data_array)     # NumPy float64
    }
    # TypeError: Object of type float64 is not JSON serializable
    return json.dumps(result)
```

**Problems:**
- NumPy types (int64, float64, etc.) are not JSON serializable
- Runtime errors when trying to serialize
- Data loss or corruption in API responses

#### ✅ Good Pattern
```python
import json
import numpy as np

def convert_numpy_types(obj):
    """Convert NumPy types to Python native types."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

def process_data_good(data_array):
    result = {
        "mean": float(np.mean(data_array)),  # Explicit conversion
        "std": float(np.std(data_array)),
        "max": float(np.max(data_array))
    }
    return json.dumps(result)  # Works correctly
```

**Benefits:**
- No runtime serialization errors
- Portable JSON that works across systems
- Clear data type handling

---

### 2. Bounds Checking Before List Access

#### ❌ Bad Pattern
```python
def get_first_item_bad(items):
    # No bounds checking - crashes on empty list
    return items[0]  # IndexError if items is empty
```

**Problems:**
- IndexError on empty lists
- No graceful error handling
- Service crashes instead of handling edge cases

#### ✅ Good Pattern
```python
import logging

logger = logging.getLogger(__name__)

def get_first_item_good(items):
    """Get first item with bounds checking."""
    if not items:
        logger.debug("List is empty, returning None")
        return None
    return items[0]
```

**Benefits:**
- No crashes on empty lists
- Graceful degradation
- Debugging information via logging
- Clear return value contracts

---

### 3. Specific Exceptions, Not Bare Except

#### ❌ Bad Pattern
```python
def parse_config_bad(config_str):
    try:
        config = json.loads(config_str)
        return config["database"]["host"]
    except:  # Catches EVERYTHING including KeyboardInterrupt
        print("Error parsing config")
        return None
```

**Problems:**
- Catches system exceptions (KeyboardInterrupt, SystemExit)
- Hides bugs and makes debugging harder
- Can't differentiate between error types
- Silent failures

#### ✅ Good Pattern
```python
import json
import logging

logger = logging.getLogger(__name__)

def parse_config_good(config_str):
    """Parse configuration with specific exception handling."""
    try:
        config = json.loads(config_str)
        return config["database"]["host"]
    except json.JSONDecodeError as e:
        logger.debug(f"Invalid JSON format: {e}")
        return None
    except KeyError as e:
        logger.debug(f"Missing configuration key: {e}")
        return None
    except TypeError as e:
        logger.debug(f"Type error in configuration: {e}")
        return None
```

**Benefits:**
- Only catches expected exceptions
- Allows system interrupts to work
- Better error messages for debugging
- Different handling per error type
- Proper logging context

---

### 4. Logger.debug() Instead of Print()

#### ❌ Bad Pattern
```python
def debug_processing_bad(data):
    print(f"Processing data: {data}")  # Goes to stdout
    print(f"Data type: {type(data)}")
    
    result = len(data) if hasattr(data, "__len__") else 0
    print(f"Result: {result}")
    return result
```

**Problems:**
- Output mixed with application output
- No log levels or filtering
- Can't disable in production
- Not captured by log aggregation systems
- No timestamps or context

#### ✅ Good Pattern
```python
import logging

logger = logging.getLogger(__name__)

def debug_processing_good(data):
    """Debug processing using proper logging."""
    logger.debug(f"Processing data: {data}")
    logger.debug(f"Data type: {type(data)}")
    
    result = len(data) if hasattr(data, "__len__") else 0
    logger.debug(f"Result: {result}")
    return result
```

**Benefits:**
- Configurable log levels (DEBUG, INFO, WARNING, ERROR)
- Can be disabled in production
- Captured by log aggregation (CloudWatch, Splunk, etc.)
- Includes timestamps and module context
- Searchable and filterable

---

### 5. Metadata-Based Categorization Over String Matching

#### ❌ Bad Pattern
```python
def categorize_by_name_bad(item_name):
    """Categorize by searching strings in name."""
    if "urgent" in item_name.lower():
        return "high_priority"
    elif "important" in item_name.lower():
        return "medium_priority"
    elif "low" in item_name.lower():
        return "low_priority"
    else:
        return "unknown"
```

**Problems:**
- Fragile string matching
- False positives ("I have low confidence" → "low_priority")
- Language-dependent
- Hard to maintain and extend
- No clear data contract

#### ✅ Good Pattern
```python
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def categorize_by_metadata_good(item: Dict[str, Any]) -> str:
    """Categorize items by metadata instead of string matching."""
    priority = item.get("priority")
    if priority is not None:
        if priority >= 9:
            return "high_priority"
        elif priority >= 5:
            return "medium_priority"
        else:
            return "low_priority"
    
    # Fallback to category metadata
    return item.get("category", "unknown")
```

**Benefits:**
- Explicit metadata contracts
- No false positives from string matching
- Language-agnostic
- Easy to extend with new categories
- Clear business logic
- Type-safe with proper validation

---

### 6. Proper Temp File Handling

AI often uses `None` for file descriptors or forgets proper cleanup. This pattern ensures safe temp file handling.

#### ❌ Bad Pattern
```python
import tempfile

def write_temp_file_bad(data):
    # BAD: Using deprecated mktemp (insecure)
    path = tempfile.mktemp()
    
    # BAD: No error handling, no cleanup on failure
    with open(path, 'wb') as f:
        f.write(data)
    
    # BAD: File is not cleaned up - left on disk
    return path
```

**Problems:**
- `mktemp` is deprecated and has security issues (race conditions)
- No error handling if write fails
- File is never cleaned up
- File descriptor not properly managed

#### ✅ Good Pattern
```python
import os
import tempfile
import logging

logger = logging.getLogger(__name__)

def write_temp_file_good(data: bytes) -> tuple[str, bool]:
    """Write data to a temporary file with proper cleanup."""
    fd = None
    path = None
    try:
        # GOOD: Use mkstemp which returns both fd and path
        fd, path = tempfile.mkstemp(suffix=".tmp")
        
        # GOOD: Use os.fdopen to convert fd to file object
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
            fd = None  # fd is now managed by the file object
        
        logger.debug(f"Successfully wrote {len(data)} bytes to {path}")
        return path, True
        
    except (IOError, OSError) as e:
        logger.debug(f"Failed to write temp file: {e}")
        # GOOD: Clean up on error
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        if path is not None and os.path.exists(path):
            try:
                os.unlink(path)
            except OSError:
                pass
        return "", False

def cleanup_temp_file_good(path: str) -> bool:
    """Clean up a temporary file safely."""
    if not path:
        return True
    try:
        if os.path.exists(path):
            os.unlink(path)
        return True
    except OSError as e:
        logger.debug(f"Failed to cleanup temp file {path}: {e}")
        return False
```

**Benefits:**
- Secure temp file creation with `mkstemp`
- Proper file descriptor management
- Cleanup on both success and failure
- Safe cleanup function for later use
- Specific exception handling

---

### 7. Large File Processing (up to 800MB)

For audio processing workflows with large files, nginx defaults block uploads and memory can be exhausted.

#### ❌ Bad Pattern
```python
def process_large_file_bad(file_path):
    # BAD: Reading entire file into memory at once
    # This will crash for 800MB files
    with open(file_path, 'rb') as f:
        data = f.read()  # Could cause MemoryError
    
    # BAD: No file size validation
    return {"size": len(data)}
```

**Problems:**
- Memory exhaustion for large files
- No size validation before processing
- No chunked reading strategy
- Will crash servers with limited memory

#### ✅ Good Pattern
```python
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def process_large_file_good(
    file_path: str,
    max_size_bytes: int = 800 * 1024 * 1024,  # 800MB default
    chunk_size: int = 1024 * 1024  # 1MB chunks
) -> Optional[Dict[str, Any]]:
    """Process large files with proper memory management."""
    try:
        # GOOD: Check file size before loading
        file_size = os.path.getsize(file_path)
        
        if file_size > max_size_bytes:
            logger.debug(f"File too large: {file_size} > {max_size_bytes}")
            return None
        
        # GOOD: Calculate chunks from file size (efficient)
        # For actual processing, read in chunks to avoid memory exhaustion
        chunks_needed = (file_size + chunk_size - 1) // chunk_size if file_size > 0 else 1
        
        return {
            "file_path": file_path,
            "size_bytes": int(file_size),  # Ensure Python int for JSON
            "size_mb": float(file_size / (1024 * 1024)),
            "chunks_needed": int(chunks_needed)
        }
        
    except FileNotFoundError:
        logger.debug(f"File not found: {file_path}")
        return None
    except (IOError, OSError) as e:
        logger.debug(f"Error processing file: {e}")
        return None
```

**Benefits:**
- Size validation before processing
- Efficient chunk calculation without reading entire file
- Proper error handling for missing files
- JSON-safe numeric types
- Configurable size limits and chunk sizes

**nginx Configuration (Required for Large Uploads):**
```nginx
# Set in nginx.conf or server block
client_max_body_size 800M;
```

**Docker SSL Note:**
```dockerfile
# AI often forgets ca-certificates for HTTPS
RUN apk add --no-cache ca-certificates
```

---

### 8. FastAPI Streaming File Uploads (Critical for Large Files)

AI often uses `file.read()` which loads entire files into memory, causing OOM errors for 800MB files.

#### ❌ Bad Pattern
```python
from fastapi import UploadFile

async def upload_audio_bad(file: UploadFile):
    # BAD: Loads entire 800MB file into memory at once
    content = await file.read()  # Will crash with MemoryError
    
    # BAD: No size validation
    # BAD: No cleanup of temp files
    with open("/tmp/audio.wav", "wb") as f:
        f.write(content)
    
    return {"size": len(content)}
```

**Problems:**
- Memory exhaustion for large files (800MB)
- No size limits enforced
- No temp file cleanup
- No file type validation
- Will crash production servers

#### ✅ Good Pattern
```python
import os
import shutil
import tempfile
from typing import Tuple
from fastapi import UploadFile, HTTPException

async def stream_upload_to_disk(
    file: UploadFile,
    max_size_bytes: int = 800 * 1024 * 1024,  # 800MB
    chunk_size: int = 1024 * 1024  # 1MB chunks
) -> Tuple[str, bool]:
    """Stream file to disk without loading into memory."""
    fd = None
    path = None
    bytes_written = 0
    
    try:
        # GOOD: Secure temp file creation
        fd, path = tempfile.mkstemp(suffix=".tmp")
        
        # GOOD: Stream in chunks
        with os.fdopen(fd, 'wb') as tmp_file:
            fd = None
            
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                
                bytes_written += len(chunk)
                
                # GOOD: Check size during streaming
                if bytes_written > max_size_bytes:
                    raise HTTPException(413, "File too large")
                
                tmp_file.write(chunk)
        
        return path, True
        
    except HTTPException:
        raise
    except (IOError, OSError) as e:
        raise HTTPException(500, f"Upload failed: {e}")
    finally:
        # GOOD: Cleanup on error
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
```

**Benefits:**
- Never loads entire file into memory
- Size validation during upload (not after)
- Proper temp file handling with cleanup
- Handles errors gracefully
- Production-safe for 800MB files

**Required nginx Configuration:**
```nginx
server {
    # CRITICAL: Default is 1MB which blocks large uploads
    client_max_body_size 800M;
    
    # CRITICAL: Increase timeouts for large uploads
    client_body_timeout 300s;
    proxy_read_timeout 300s;
    
    # CRITICAL: Disable buffering for streaming
    proxy_request_buffering off;
}
```

**Required Docker Configuration:**
```dockerfile
FROM python:3.11-alpine

# CRITICAL: AI often forgets ca-certificates
# Causes SSL verification failures
RUN apk add --no-cache ca-certificates

# Rest of Dockerfile...
```

---

### 9. NumPy NaN/Inf Handling in Audio Processing

Audio processing often produces NaN or Inf values that cause JSON serialization to fail silently.

#### ❌ Bad Pattern
```python
import numpy as np
import json

def analyze_audio_bad(samples):
    # Audio processing might produce NaN/Inf
    result = {
        "peak": np.max(samples),  # Could be Inf
        "rms": np.sqrt(np.mean(samples**2)),  # Could be NaN
        "duration": np.float64(len(samples) / 44100)
    }
    # json.dumps() will fail or produce invalid JSON
    return json.dumps(result)
```

**Problems:**
- NaN and Inf are not valid JSON
- Silent failures or invalid responses
- Breaks API contracts
- Hard to debug in production

#### ✅ Good Pattern
```python
import numpy as np
import json
from typing import Any, Dict

def convert_numpy_audio_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Convert audio results with NaN/Inf handling."""
    def convert_value(val: Any) -> Any:
        if isinstance(val, np.integer):
            return int(val)
        elif isinstance(val, np.floating):
            # GOOD: Handle NaN and Inf explicitly
            if np.isnan(val):
                return None  # or 0.0, depending on API contract
            elif np.isinf(val):
                return None  # or max/min value
            return float(val)
        elif isinstance(val, np.ndarray):
            return val.tolist()
        elif isinstance(val, dict):
            return {k: convert_value(v) for k, v in val.items()}
        elif isinstance(val, list):
            return [convert_value(item) for item in val]
        return val
    
    return convert_value(result)

def analyze_audio_good(samples):
    result = {
        "peak": np.max(samples),
        "rms": np.sqrt(np.mean(samples**2)),
        "duration": len(samples) / 44100
    }
    # GOOD: Convert with NaN/Inf handling before JSON
    safe_result = convert_numpy_audio_result(result)
    return json.dumps(safe_result)
```

**Benefits:**
- Explicit handling of edge cases (NaN, Inf)
- Valid JSON output guaranteed
- Clear API contract (NaN/Inf → None)
- Recursive handling of nested structures
- Production-safe audio processing

---

## Multi-Agent Review Pattern & Ensemble Reasoning

### Sequential Review (Current Pattern)

Use multiple AI agents for better code quality:

```
┌──────────────────┐     ┌──────────────────┐
│   Agent 1        │     │   Agent 2        │
│   (Generator)    │────►│   (Reviewer)     │
│   Creates code   │     │   Critiques it   │
└──────────────────┘     └──────────────────┘
         │                        │
         ▼                        ▼
┌─────────────────────────────────────────────┐
│              Human Decision                  │
│   Accept / Modify / Request Alternative     │
└─────────────────────────────────────────────┘
```

### Ensemble Reasoning (Advanced Pattern)

For critical decisions or when AI confidence is low, use ensemble reasoning across multiple models:

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Claude     │  │   GPT-4      │  │   Gemini     │
│   Output A   │  │   Output B   │  │   Output C   │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └────────────────┼────────────────┘
                        ▼
              ┌─────────────────┐
              │  Convergence    │
              │  Analysis       │
              │  (Human-led)    │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Interpretation  │
              └─────────────────┘

Key Insights:
• Disagreement = signal for deeper investigation
• Convergence = higher confidence (but not certainty)
• Human judges which model's reasoning applies to this context
```

**When to Use Ensemble Reasoning:**

| Situation | Single Model | Ensemble |
|-----------|-------------|----------|
| Boilerplate code | ✓ Sufficient | Overkill |
| Critical security logic | Consider | ✓ **Recommended** |
| Novel problem domain | Consider | ✓ **Recommended** |
| AI confidence low (CALIBRATE stage) | May miss issues | ✓ **Use ensemble** |
| High failure severity (CALIBRATE stage) | Risky | ✓ **Use ensemble** |
| Financial compliance code | Single pass risky | ✓ **Required** |

**Ensemble Analysis Process:**

1. **Generate:** Get outputs from 2-3 different AI models for same prompt
2. **Compare:** Identify points of agreement and disagreement
3. **Investigate Disagreements:** These often reveal edge cases or ambiguities
4. **Synthesize:** Human selects best elements from each, or identifies need for more research
5. **Document:** Record what caused disagreement for future pattern refinement

**Example Ensemble Prompt:**
```
Problem: Implement rate limiting for API endpoint handling 800MB uploads

Requirements:
- Prevent abuse while allowing legitimate large files
- Consider nginx + application-level coordination
- Must handle client disconnects gracefully

[Send same prompt to Claude, GPT-4, Gemini]
```

**Handling Ensemble Disagreements:**

- **All agree:** High confidence, proceed (but still verify)
- **2/3 agree:** Examine dissenting view for edge cases it caught
- **All disagree:** Problem is under-specified, return to DEFINE stage
- **One clearly wrong:** Use as negative example to refine prompts

**Managing API Rate Limits:**

When using multiple AI services for ensemble reasoning:
- Space requests 1-2 seconds apart to avoid rate limiting
- Cache ensemble results for repeated similar queries
- Rotate models based on which aspects they excel at:
  - Claude: Nuanced reasoning, code quality
  - GPT-4: Broad pattern matching, API knowledge
  - Gemini: Performance optimization, system design
- Monitor token usage across providers to manage costs

---

### Review Prompt Template

```
Review this code for:
1. Security issues (especially input validation)
2. Error handling gaps
3. Performance concerns for large files (up to 800MB)
4. Testing blind spots
5. Domain-specific correctness (audio processing, compliance)

Context:
- Use case: [specific scenario]
- Constraints: [specific constraints]
- Compliance requirements: [if applicable]

Code:
[paste code]
```

---

## Context Hygiene Protocol

For long development sessions, context degradation is real and causes AI to "forget" earlier decisions or constraints.

### Context Refresh Cadence

**Every 3-4 exchanges:**
- Summarize decisions made → feed back as compressed context
- Explicitly state what's STILL relevant vs. deprecated
- Prune outdated information from conversation

**Signs Context is Degrading:**
- AI suggests something you already rejected
- AI "forgets" constraints you mentioned earlier
- AI contradicts earlier parts of the conversation
- Responses become more generic

### Session Checkpoint Prompt

Use this every 3-4 exchanges or when you notice degradation:

```
⏸️ CHECKPOINT: Before continuing, please summarize our current state:

1. Problem: [What are we solving?]
2. Decisions made: [Key choices and rationale]
3. Constraints still active: [What bounds our solution?]
4. Next action: [What's the immediate next step?]

I'll verify accuracy before we continue.
```

### Fresh Start Pattern

**When to use:** Context is too polluted, session has veered off course, or you've hit the same issue 3+ times.

**How to do it:**
1. Stop the current session
2. Write a clean problem statement incorporating all learnings
3. Start new session with compressed context
4. Reference previous session ID for continuity if needed

**Example Fresh Start Prompt:**
```
Fresh start on [problem]. Previous session got bogged down in [issue].

Context from previous session:
- Tried: [approach], failed because [reason]
- Learned: [key insight]
- Constraint: [specific constraint]

Current goal: [clear, focused objective]

Please suggest approach considering above learnings.
```

### Context Compression Technique

For long sessions, periodically compress context:

**Before (Verbose):**
> "We tried using file.read() but that didn't work for large files. Then we tried chunked reading but had issues with memory. We discussed various chunk sizes like 1MB and 512KB. Eventually we settled on streaming with 1MB chunks and proper error handling."

**After (Compressed):**
> "✓ Decision: Stream uploads in 1MB chunks (not file.read()). Rationale: 800MB files + memory constraints. Implementation verified."

**Compression Template:**
```
✓ Decision: [What was decided]
✗ Rejected: [What didn't work and why]
⚠️ Active Constraint: [What still limits us]
→ Next: [Immediate next action]
```

---

## Iteration Loop Example

### ORIENT Phase
1. Check mental models and assumptions
2. Verify you're solving the right problem
3. Identify active constraints (time, compliance, resources)
4. Articulate success criteria

### DEFINE Phase
1. Identify the pattern or problem
2. Research best practices (use AI for possibility space)
3. Filter solutions based on domain constraints (human judgment)
4. Define measurable success criteria
5. If later stages reveal wrong assumptions, loop back here

### DESIGN Phase
1. Generate design alternatives (AI assists)
2. Evaluate against maintenance burden and team expertise (human decides)
3. Consider domain-specific constraints
4. Document design decisions and rationale

### BUILD Phase
1. Implement the minimal solution
2. Focus on one pattern at a time
3. Add type hints for clarity
4. Write clear docstrings
5. Use AI for speed, verify domain correctness yourself

### VERIFY Phase
1. Run automated tests
2. Check code coverage
3. Review against style guide
4. Look for edge cases (AI generates, human validates)
5. Verify logging and error handling

### CALIBRATE Phase
1. Rate AI confidence level (Low/Medium/High)
2. Assess domain fit (Poor/Fair/Good)
3. Evaluate failure severity (Low/Medium/High/Critical)
4. Decide: human deep review, extra tests, or automated verification
5. For critical + low confidence: use ensemble reasoning

### HARDEN Phase
1. Security review (use tools: CodeQL, Coderabbit)
2. Compliance validation (SAR requirements, audit trails)
3. Performance testing under load
4. Error recovery and resilience
5. Documentation and runbooks

### Retrospective Phase
1. What worked well?
2. What could be improved?
3. What patterns emerged?
4. What should be documented?
5. Update this document with learnings
6. Update prompt changelog with effective prompts

---

## Failure Escalation Protocol

**What happens when gates fail repeatedly?**

AI-generated solutions don't always work on the first try. Use this escalation protocol to avoid spinning:

### Escalation Ladder

**Gate fails 1x:**
- Review error message carefully
- Check if prompt was clear and specific
- Verify all constraints were communicated

**Gate fails 2x:**
- **→ Decompose task further**
- Break into smaller, more specific sub-tasks
- Focus AI on one aspect at a time
- Example: Instead of "implement auth", try "validate JWT signature only"

**Gate fails 3x:**
- **→ Switch tools/models entirely**
- Try different AI model (e.g., Claude → GPT-4)
- Use ensemble reasoning to identify disconnect
- Consult documentation directly instead of asking AI

**Gate fails 4x:**
- **→ Fundamental constraint missed in ORIENT/DEFINE**
- Return to ORIENT stage
- Question: Are we solving the right problem?
- Check for hidden assumptions or unstated requirements
- May need to reframe the entire approach

**Gate fails 5x:**
- **→ STOP. Rubber duck with human.**
- Problem is likely misframed or underspecified
- AI cannot help until problem is clarified
- Seek human expert in the domain
- Document what doesn't work to avoid future attempts

### Example Escalation in Practice

**Scenario:** AI keeps generating FastAPI upload code that fails for 800MB files

- **Fail 1:** "AI used file.read()" → Try again with "use streaming"
- **Fail 2:** "Still memory issues" → Decompose: "Show just the chunk reading loop"
- **Fail 3:** "Chunk logic works but nginx blocks" → Switch focus: "What nginx config allows 800MB?"
- **Fail 4:** "nginx config conflicts with SSL" → Return to ORIENT: "What's the actual deployment stack?" (turns out using cloudflare proxy with different limits)
- **Fail 5:** → STOP, talk to DevOps human who knows the production environment

**Key Insight:** Failure escalation is not weakness—it's efficient problem-solving. Recognize when to stop and reframe.

---

## Results Documentation

### Test Coverage
All nine patterns have comprehensive test coverage:
- ✅ NumPy type conversion: 5 tests
- ✅ Bounds checking: 4 tests
- ✅ Specific exceptions: 4 tests
- ✅ Logger usage: 3 tests
- ✅ Metadata categorization: 6 tests
- ✅ Temp file handling: 4 tests
- ✅ Large file processing: 4 tests
- ✅ FastAPI streaming uploads: 25 tests (including adversarial cases)
- ✅ NumPy NaN/Inf handling: 5 tests (within FastAPI tests)

**Total: 60 tests covering all critical paths**

**New Adversarial Tests (Phase 5 from problem statement):**
- ✅ 800MB silent file (all zeros) handling
- ✅ White noise file (random data) handling  
- ✅ Client disconnect mid-upload simulation
- ✅ Disk full error (OSError) during write
- ✅ NaN and Inf value serialization
- ✅ Invalid file extension rejection
- ✅ Permission denied errors
- ✅ Zero-byte file handling

### Good Results
✅ **Type Safety**: No runtime JSON serialization errors  
✅ **Robustness**: Graceful handling of empty lists  
✅ **Debuggability**: Specific exception messages aid troubleshooting  
✅ **Observability**: Structured logging enables monitoring  
✅ **Maintainability**: Metadata-based logic is easy to extend  
✅ **File Safety**: Proper temp file handling with cleanup  
✅ **Memory Safety**: Large files processed in chunks  

### Bad Results (Before Improvements)
❌ **Type Errors**: JSON serialization crashes with NumPy types  
❌ **Index Errors**: Empty list access crashes services  
❌ **Silent Failures**: Bare except hides real problems  
❌ **Poor Logging**: Print statements not captured in production  
❌ **Fragile Logic**: String matching causes false categorizations  
❌ **File Leaks**: Temp files left on disk without cleanup  
❌ **Memory Exhaustion**: Large files loaded entirely into memory  

---

## 📊 Workflow Metrics I Track

| Metric | What It Tells Me | How to Improve |
|--------|------------------|----------------|
| AI suggestions accepted as-is | Am I prompting effectively? | → Review Prompt Changelog for effective patterns |
| Bugs from AI code | What patterns to verify? | → Add to Domain-Specific Blind Spots section |
| Time to working feature | Is the workflow efficient? | → Check if stuck at same stage (use Failure Escalation) |
| Rework after review | Where are the gaps? | → CALIBRATE stage catches these earlier |
| Gate failures per stage | Which stage needs better process? | → ORIENT failures = wrong problem, BUILD failures = unclear prompts |
| Ensemble agreement rate | How confident should I be? | → Low agreement = return to DEFINE |

**Weekly Review Process:**

1. Review Prompt Changelog: Which prompts worked? Which failed?
2. Review Domain Blind Spots: Did AI make same mistakes? Update checklist.
3. Review Failure Escalations: Did I stop at appropriate level?
4. Update AI_PATTERNS.md with new learnings
5. Identify one process improvement for next week

**Connection to Metrics:**
- Prompt changelog → Improves "AI suggestions accepted as-is"
- Domain blind spots → Reduces "Bugs from AI code"
- Failure escalation → Improves "Time to working feature"
- CALIBRATE stage → Reduces "Rework after review"

---

## 🧠 Lessons Learned

### Things AI Consistently Gets Wrong (for me)

**See "Domain-Specific AI Blind Spots" section for detailed examples.**

1. **numpy → JSON serialization** - Always check, especially NaN/Inf values
2. **Docker SSL certificates** - Always add ca-certificates
3. **File descriptor handling** - Always use proper fd patterns
4. **nginx defaults** - Always set client_max_body_size
5. **FastAPI file uploads** - Uses `file.read()` instead of streaming (CRITICAL for 800MB files)
6. **Temp file cleanup** - Forgets `finally` blocks with `os.unlink()`
7. **Async/await patterns** - Misses await in async functions
8. **Audio array dimensions** - Assumes wrong shape for sample rate derivation
9. **FFT windowing** - Uses default overlap instead of domain-appropriate settings
10. **Compliance formatting** - Returns generic output instead of SAR-compliant structure
11. **Cross-jurisdiction rules** - Misses "most restrictive jurisdiction" principle

**→ Action:** When AI makes these mistakes, log in Prompt Changelog and update prompts to be explicit.

### Things AI Does Well

1. **Boilerplate generation** - FastAPI endpoints, Pydantic models
2. **Test case generation** - Given good examples
3. **Documentation** - Docstrings, README sections
4. **Refactoring** - When given clear patterns to follow
5. **Exploring possibilities** - Generating alternatives in DEFINE/DESIGN stages
6. **Code review** - Finding common issues (when prompted with specific checklist)

**→ Leverage:** Use AI heavily for these tasks, verify output quickly and move on.

---

## Quick Reference

### When to Use Each Pattern

| Pattern | Use When | Don't Use When |
|---------|----------|----------------|
| NumPy conversion | Using NumPy with JSON APIs | Pure Python types only |
| Bounds checking | Accessing list/array elements | Length already verified |
| Specific exceptions | Handling expected errors | Re-raising all exceptions |
| Logger.debug() | Adding debug information | User-facing messages |
| Metadata categorization | Complex business logic | Simple true/false checks |
| Temp file handling | Working with temporary files | In-memory processing sufficient |
| Large file processing | Files > 10MB or memory constrained | Small files in memory OK |
| FastAPI streaming | Files > 10MB, especially audio/video | Small uploads < 1MB |
| NaN/Inf handling | Audio processing, scientific computing | Integer-only data |

---

## Prompt Engineering Tips

### Design & Planning Prompt Pattern

Use this pattern for AI-assisted design:

```
I'm building [specific feature].

Context:
- Tech: FastAPI, Docker, nginx
- Constraint: [specific constraint]
- Existing pattern: [reference to codebase]

Help me design the approach. Consider:
1. Edge cases
2. Error handling
3. Testing strategy
```

### AI Output Review Checklist

- [ ] Does it align with my existing patterns?
- [ ] Are the dependencies appropriate?
- [ ] Did it miss any constraints I mentioned?

### For Better AI Assistance
1. **Be Specific**: "Convert NumPy float64 to Python float before JSON" vs "Fix JSON"
2. **Provide Context**: Include error messages and stack traces
3. **Show Examples**: Demonstrate input/output expectations
4. **Request Tests**: Ask for test cases alongside implementation
5. **Iterate**: Refine based on results, don't expect perfection first try

### Example Prompts

**Bad Prompt:**
> "Fix the JSON problem"

**Good Prompt:**
> "I'm getting 'TypeError: Object of type float64 is not JSON serializable' when serializing NumPy arrays. Please show how to convert NumPy types to Python native types before JSON serialization, with tests."

**Bad Prompt:**
> "Add error handling"

**Good Prompt:**
> "Replace bare `except:` clauses with specific exception handling for JSON parsing errors (JSONDecodeError), missing keys (KeyError), and type errors (TypeError). Use logger.debug() to log each case with context."

### When AI Gets It Wrong

**Pattern: Clarify and Constrain**
```
That solution doesn't handle [specific case].

Additional context:
- We're using [specific library/pattern]
- The constraint is [specific constraint]
- Here's an example that does work: [code snippet]

Please revise.
```

### When AI Gets It Right

**Document for future sessions:**
```
This pattern works well for [use case]:
[code snippet with comments]

Key insight: [what made this work]
```

---

## Prompt Evolution Tracking

**Problem:** You iterate prompts, but without version control you lose track of what works.

**Solution:** Maintain a prompt changelog for institutional memory.

### Prompt Changelog Template

| Date | Stage | Old Prompt | New Prompt | Why Changed | Effectiveness |
|------|-------|------------|------------|-------------|---------------|
| 2024-01-15 | VERIFY | "Review this code" | "Review for: 1) Security 2) 800MB file handling 3) NumPy edge cases" | Generic reviews missed domain issues | ✓ Caught NaN bug |
| 2024-01-20 | BUILD | "Create upload handler" | "Create FastAPI upload handler that STREAMS 800MB files in 1MB chunks to temp file using mkstemp" | AI kept using file.read() | ✓ Works first try |
| 2024-01-25 | DESIGN | "How should I structure this?" | "FastAPI app structure following 12-factor app principles, specifically: [list constraints]" | Too vague, got generic advice | ✓ Domain-specific design |
| 2024-02-01 | HARDEN | "Check for security issues" | "Security review for: 1) Input validation (file size, type) 2) Injection risks 3) DoS via large files" | Missed file-specific vectors | ✓ Found size limit gap |

**How to Use:**
1. When a prompt works well → log it
2. When a prompt fails → log why and what you changed
3. Review monthly to identify patterns
4. Share effective prompts with team
5. Build a prompt library for common tasks

**Example Prompt Library Entry:**

```markdown
### Prompt: FastAPI Large File Upload (Proven)

**Use for:** Implementing file upload endpoints for files > 100MB

**Prompt:**
"Create a FastAPI endpoint that:
1. Streams file to disk (no memory loading)
2. Uses tempfile.mkstemp() for secure temp files
3. Validates size during upload (fail fast at [X]MB)
4. Returns temp file path or error
5. Include proper cleanup in finally block

Requirements: Handle up to [X]MB, chunk size [Y]MB"

**Effectiveness:** ✓ Works first try with Claude, needs minor tweaks with GPT-4
**Last Updated:** 2024-02-01
**Gotchas:** Remember to configure nginx client_max_body_size
```

---

## Security & Compliance Deep Dive

### Generic Web Security (Standard)

- ✓ Input validation
- ✓ SQL injection prevention
- ✓ XSS protection
- ✓ CSRF tokens
- ✓ Authentication & authorization

**AI handles these reasonably well with standard prompts.**

### Domain-Specific Security (Critical for Financial Compliance)

**AI often misses these without explicit prompting:**

#### 1. Audit Trail Completeness

**Requirement:** Regulators must be able to reconstruct all decisions.

```python
import logging
from datetime import datetime
from typing import Dict, Any
import json

logger = logging.getLogger(__name__)

def log_audit_event(
    event_type: str,
    user_id: str,
    action: str,
    resource: str,
    result: str,
    metadata: Dict[str, Any]
) -> None:
    """Log audit event for regulatory compliance.
    
    All fields required for reconstruction of decision trail.
    """
    audit_entry = {
        "timestamp_utc": datetime.utcnow().isoformat(),
        "event_type": event_type,  # e.g., "analysis", "decision", "data_access"
        "user_id": user_id,  # Who performed action
        "action": action,  # What they did
        "resource": resource,  # What they acted on (file path, record ID)
        "result": result,  # Success, failure, error
        "metadata": metadata,  # Additional context
        "version": "1.0",  # Audit log schema version
    }
    
    # CRITICAL: Structured logging for audit aggregation
    logger.info(f"AUDIT: {json.dumps(audit_entry)}")
    
    # CRITICAL: Also write to append-only audit database
    # (not shown here, but required for compliance)
```

**Key Requirements AI Misses:**
- Who, what, when, where, why for every action
- Immutable audit logs (append-only)
- Tamper-evident storage
- Retention period compliance (often 5-7 years)

---

#### 2. Explainability Requirements

**Requirement:** Black-box ML is not acceptable for SAR (Suspicious Activity Reports).

```python
from typing import Dict, List, Any

def generate_explainable_decision(
    input_data: Dict[str, Any],
    model_output: Dict[str, float],
    threshold: float,
    features_used: List[str]
) -> Dict[str, Any]:
    """Generate explainable decision for regulatory review.
    
    Regulators require understanding of how decision was made.
    """
    # Calculate feature importance (simplified)
    explanations = []
    
    for feature in features_used:
        contribution = model_output.get(f"{feature}_score", 0.0)
        if abs(contribution) > 0.1:  # Significant contribution
            explanations.append({
                "feature": feature,
                "contribution": float(contribution),
                "interpretation": _interpret_feature(feature, contribution)
            })
    
    return {
        "decision": "SUSPICIOUS" if model_output["score"] > threshold else "CLEAR",
        "confidence": float(model_output["score"]),
        "threshold": threshold,
        "explanations": explanations,
        "human_readable": _generate_narrative(explanations),
        # CRITICAL: Enough detail for non-technical regulator to understand
    }

def _interpret_feature(feature: str, contribution: float) -> str:
    """Convert technical feature to plain language."""
    interpretations = {
        "spectral_anomaly": "Voice frequency patterns inconsistent with natural speech",
        "phase_coherence": "Audio phase relationships suggest digital editing",
        "background_noise": "Background acoustic signature anomalous",
    }
    return interpretations.get(feature, f"Feature {feature} contributed {contribution}")

def _generate_narrative(explanations: List[Dict]) -> str:
    """Create plain-language explanation for regulators."""
    parts = ["Analysis indicates suspicious activity based on: "]
    for exp in explanations:
        parts.append(f"{exp['interpretation']}. ")
    return "".join(parts)
```

**Why This Matters:**
- Regulators are not ML experts
- "The model said so" is not sufficient
- Must explain in domain terms (voice patterns, not neural activations)
- Explanation must be reproducible from audit trail

---

#### 3. Data Retention & Destruction Policies

**Requirement:** Must keep data for X years, then must destroy per regulation.

```python
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class RetentionPolicy:
    """Enforce data retention and destruction policies.
    
    Different data types have different retention requirements.
    """
    
    RETENTION_PERIODS = {
        "sar_report": timedelta(days=5*365),  # 5 years for SARs
        "audit_log": timedelta(days=7*365),   # 7 years for audit logs
        "customer_data": timedelta(days=5*365),  # 5 years after relationship ends
        "analysis_temp": timedelta(days=90),  # 90 days for working files
    }
    
    @staticmethod
    def should_destroy(
        data_type: str,
        created_date: datetime,
        relationship_end_date: Optional[datetime] = None
    ) -> bool:
        """Check if data should be destroyed per policy."""
        retention_period = RetentionPolicy.RETENTION_PERIODS.get(data_type)
        if retention_period is None:
            logger.warning(f"Unknown data type: {data_type}, defaulting to no destruction")
            return False
        
        # For customer data, retention starts after relationship ends
        if data_type == "customer_data" and relationship_end_date:
            reference_date = relationship_end_date
        else:
            reference_date = created_date
        
        expiry_date = reference_date + retention_period
        return datetime.utcnow() > expiry_date
    
    @staticmethod
    def destroy_data(
        file_path: str,
        data_type: str,
        record_id: str
    ) -> bool:
        """Destroy data and log for audit."""
        import os
        
        try:
            # CRITICAL: Log before destruction (audit trail)
            logger.info(f"DESTRUCTION: type={data_type}, record={record_id}, path={file_path}")
            
            # Secure deletion (overwrite before unlink for sensitive data)
            if os.path.exists(file_path):
                # For production: use secure deletion library
                os.unlink(file_path)
            
            # CRITICAL: Log after destruction (confirmation)
            logger.info(f"DESTROYED: type={data_type}, record={record_id}")
            return True
            
        except Exception as e:
            logger.error(f"DESTRUCTION_FAILED: {data_type}/{record_id}: {e}")
            return False
```

**Key Points AI Misses:**
- Different retention periods for different data types
- Retention clock starts at different points (creation vs. relationship end)
- Must LOG destruction attempts for audit
- Secure deletion required for PII/sensitive data
- Automated retention enforcement (not manual)

---

#### 4. Cross-Jurisdictional Compliance

**Problem:** State vs. Federal regulations may conflict or have different requirements.

**Example: Audio Consent Laws**

```python
from enum import Enum
from typing import Set

class ConsentRequirement(Enum):
    ONE_PARTY = "one_party"    # One party must consent (federal)
    TWO_PARTY = "two_party"    # All parties must consent (CA, FL, etc.)
    ALL_PARTY = "all_party"    # All parties must consent (stricter)

class JurisdictionCompliance:
    """Check compliance across multiple jurisdictions."""
    
    # State-specific requirements
    TWO_PARTY_STATES = {"CA", "FL", "PA", "IL", "MT", "WA", "MD", "MA", "NH", "CT"}
    
    @staticmethod
    def check_recording_consent(
        recording_state: str,
        participant_states: Set[str],
        consents_obtained: Set[str]
    ) -> tuple[bool, str]:
        """Check if recording consent is legally compliant.
        
        Must comply with MOST RESTRICTIVE jurisdiction involved.
        """
        # Determine most restrictive requirement
        all_states = participant_states.union({recording_state})
        requires_two_party = bool(all_states.intersection(JurisdictionCompliance.TWO_PARTY_STATES))
        
        if requires_two_party:
            # Must have consent from ALL participants
            if consents_obtained == participant_states:
                return True, "Compliant: All-party consent obtained"
            else:
                missing = participant_states - consents_obtained
                return False, f"Non-compliant: Missing consent from {missing} (two-party state involved)"
        else:
            # One-party consent sufficient
            if len(consents_obtained) >= 1:
                return True, "Compliant: One-party consent obtained"
            else:
                return False, "Non-compliant: No consent obtained"
    
    @staticmethod
    def check_data_residency(
        data_location: str,
        customer_location: str
    ) -> tuple[bool, str]:
        """Check data residency requirements.
        
        Some jurisdictions require data to stay within borders.
        """
        # EU GDPR: Data must stay in EU unless adequacy decision
        eu_countries = {"DE", "FR", "IT", "ES", "NL", "BE", "AT", "IE", "etc"}
        
        if customer_location in eu_countries:
            if data_location not in eu_countries and data_location not in {"US"}:
                # Simplified: US has adequacy framework
                return False, f"GDPR violation: EU customer data in {data_location}"
        
        return True, "Data residency compliant"
```

**AI Consistently Misses:**
- Most restrictive jurisdiction rule
- State vs. federal conflicts
- International data residency (GDPR, CCPA)
- Consent requirements vary by state
- Must check ALL participants' locations, not just one

---

### Security Checklist for HARDEN Stage

When using tools like **CodeQL** and **Coderabbit**:

**Setup Context (AI often introduces these without setup):**
- CodeQL: GitHub native, requires workflow setup in .github/workflows
- Coderabbit: Third-party code review bot, requires integration setup

**Domain-Specific Checklist:**

- [ ] **Audit Trail**: All sensitive actions logged with who/what/when/where
- [ ] **Explainability**: ML decisions have plain-language explanations
- [ ] **Data Retention**: Automated enforcement of retention policies
- [ ] **Data Destruction**: Logged and verifiable destruction after retention period
- [ ] **Cross-Jurisdiction**: Compliance checked for ALL relevant jurisdictions
- [ ] **Consent Management**: Recording consent meets most restrictive requirement
- [ ] **PII Handling**: Proper encryption at rest and in transit
- [ ] **Access Controls**: Role-based access with principle of least privilege
- [ ] **Incident Response**: Documented procedures for data breach scenarios
- [ ] **Version Tracking**: Analysis algorithm versions logged for reproducibility

**AI Assistance Limits:**
- ✓ Can generate code templates for audit logging
- ✓ Can check for common security vulnerabilities
- ✗ Cannot assess regulatory compliance (needs legal expert)
- ✗ Cannot judge "reasonable" security (context-dependent)
- ✗ Cannot determine data sensitivity classification (domain expert needed)

---

## Contributing to This Document

When you discover new patterns or improvements:

1. Follow the feedback loop: ORIENT → DEFINE → DESIGN → BUILD → VERIFY → CALIBRATE → HARDEN
2. Document both bad and good examples
3. Explain the problems and benefits
4. Add test cases demonstrating the pattern
5. Update this document in the Retrospective phase
6. Include concrete before/after results
7. **Update Prompt Changelog** with prompts that worked (or didn't)
8. Share domain-specific blind spots you discover

---

## License

This document and examples are part of the feedback-loop repository.
See LICENSE for details.
