# Water Kiosk USSD Server

A Flask-based USSD server with MTN/Airtel payment integration.

## Getting Started

### 1. Start the Virtual Environment

Before running the server, you need to activate the Python virtual environment:

```bash
source venv/bin/activate
```

You should see `(venv)` appear at the beginning of your terminal prompt, indicating the virtual environment is active.

### 2. Launch the Server

You have two options for starting the server:

**Option A: Run with MTN Mobile Money Integration**
```bash
./start_server_with_mtn.sh
```

**Option B: Run the AT Server directly**
```bash
python at_server.py
```

**Option C: Run the USSD Server directly**
```bash
python ussd_server.py
```

The server will start on port 5000 by default (or as specified in your environment variables).

### 3. Shut Down the Virtual Environment

When you're done with the server, deactivate the virtual environment:

```bash
deactivate
```

The `(venv)` prefix in your terminal prompt will disappear, indicating you've successfully exited the virtual environment.

## Summary of Commands

```bash
# Start virtual environment
source venv/bin/activate

# Launch the server (choose one)
./start_server_with_mtn.sh    # With MTN Mobile Money
python at_server.py            # AT Server
python ussd_server.py          # USSD Server

# Stop virtual environment (when done)
deactivate
```

## Requirements

- Python 3.x
- Flask 3.1.2
- Virtual environment (venv)

All dependencies are listed in `requirements.txt` and are installed when you set up the virtual environment.
