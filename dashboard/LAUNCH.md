# How to Launch the NovaOS Dashboard

## Quick Start (Easiest)

```bash
cd /Users/krissanders/novaos-v2/dashboard
./nova-dashboard start
```

Open browser: **http://localhost:5001**

## Available Commands

```bash
./nova-dashboard start   # Start server
./nova-dashboard stop    # Stop server
./nova-dashboard status  # Check if running
```

## Alternative Methods

### Method 1: Standalone Script (Recommended)
```bash
cd dashboard
./nova-dashboard start
```
- No dependencies on main CLI
- Fastest startup
- Most reliable

### Method 2: Start Script
```bash
cd dashboard
./start.sh
```
- Simple bash script
- No Python imports

### Method 3: Direct Python
```bash
cd dashboard
python3 app.py
```
- Direct Flask launch
- For development/debugging

### Method 4: Via Main CLI
```bash
cd /Users/krissanders/novaos-v2
python3 cli.py dashboard start
```
- Integrated with main CLI
- Requires all dependencies installed

## Troubleshooting

### Port Already in Use
```bash
lsof -ti:5001 | xargs kill
# Then start again
./nova-dashboard start
```

### Import Errors
Use the standalone launcher (`./nova-dashboard`) which has minimal dependencies.

### Database Not Found
Ensure database exists at:
```bash
ls -la /Users/krissanders/novaos-v2/data/novaos.db
```

## Stop Dashboard

Press `Ctrl+C` in the terminal where it's running, or:
```bash
./nova-dashboard stop
```

## Full Documentation

See [DASHBOARD.md](DASHBOARD.md) for complete documentation.
