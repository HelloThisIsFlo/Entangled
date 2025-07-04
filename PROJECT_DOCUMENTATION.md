# Entangled - Synchronized Media Playback System

## Overview

**Entangled** is a distributed media synchronization system designed to coordinate playback across multiple Plex media server clients. The system uses MQTT messaging to synchronize movie/TV show playback between different devices, enabling users to watch content together in perfect sync across multiple locations.

## Architecture

### Core Components

1. **Flask Web Server** (`entangled/server.py`)
   - Provides a web interface for controlling playback
   - Offers both production and testing modes
   - Includes debugging endpoints and mock interfaces for testing

2. **MQTT Client** (`entangled/mqtt.py`)
   - Handles message publishing and subscription
   - Supports SSL/TLS connections
   - Manages message type routing and callbacks

3. **Plex Integration** (`entangled/plex.py`)
   - Interfaces with Plex Media Server using PlexAPI
   - Provides abstract base class for different implementations
   - Includes mock implementation for testing

4. **Scheduler** (`entangled/scheduler.py`)
   - Schedules timed execution of functions
   - Handles synchronized playback timing
   - Validates scheduling constraints

5. **Configuration Management** (`entangled/config.py`)
   - Manages environment variables and settings
   - Supports multiple deployment environments
   - Configures MQTT and Plex connections

### System Flow

1. **Initialization**
   - System connects to configured Plex server
   - Establishes MQTT connection
   - Web server starts and listens for requests

2. **Synchronization Process**
   - User clicks "Play" button on web interface
   - System captures current movie time from Plex
   - Calculates synchronized play time (current time + delay)
   - Publishes MQTT message with sync information
   - All connected clients receive the message
   - Clients seek to specified movie time
   - Clients schedule simultaneous playback

3. **Message Format**
   ```json
   {
     "type": "play",
     "movieTime": "1:23:45",
     "playAt": 1606484723000
   }
   ```

## Directory Structure

```
entangled/
├── entangled/          # Main Python package
│   ├── config.py       # Configuration management
│   ├── entangled.py    # Core synchronization logic
│   ├── mqtt.py         # MQTT client implementation
│   ├── plex.py         # Plex API integration
│   ├── scheduler.py    # Task scheduling
│   ├── server.py       # Flask web server
│   └── tests/          # Unit tests
├── templates/          # HTML templates
│   ├── debug.html      # Debug interface
│   └── main_page.html  # Main user interface
├── Pipfile            # Python dependencies
├── start_for_prod.sh  # Production startup script
├── start_for_e2e.sh   # Testing startup script
└── print_all_resources.py  # Utility for listing Plex resources

mqtt/
├── config/            # MQTT configuration
├── start_mqtt.sh      # MQTT broker startup script
└── create_password_file.sh  # Password management

e2eTests/
├── cypress/           # End-to-end tests
├── package.json       # Node.js dependencies
└── yarn.lock          # Dependency lock file

experiments/           # Experimental features
├── buildExecutablesWithPython/
├── localSyncWithJS/
└── plexClientApi/
```

## Features

### Implemented Features

1. **MQTT-based Synchronization**
   - Publish/subscribe messaging for coordination
   - SSL/TLS support for secure communications
   - Message type routing and filtering

2. **Plex Integration**
   - Connect to Plex Media Server
   - Retrieve current playback position
   - Control playback (play, pause, seek)
   - Support for multiple Plex resources

3. **Web Interface**
   - Simple one-button sync interface
   - Debug panel for development
   - Mock interface for testing

4. **Timed Scheduling**
   - Precise timing for synchronized playback
   - Configurable delay buffers
   - Validation of scheduling constraints

5. **Multiple Environment Support**
   - Production mode with real Plex integration
   - Testing mode with mock implementations
   - End-to-end testing infrastructure

6. **Comprehensive Testing**
   - Unit tests for core functionality
   - End-to-end tests using Cypress
   - Mock implementations for isolated testing

## Dependencies

### Python Dependencies (via Pipfile)
- `plexapi` - Plex Media Server API client
- `flask` - Web framework
- `paho-mqtt` - MQTT client
- `pytest` - Testing framework
- `pytest-watch` - Automated test runner
- `pyyaml` - YAML configuration support
- `autopep8` - Code formatting (dev dependency)

### Node.js Dependencies (for testing)
- `cypress` - End-to-end testing framework
- `mqtt` - MQTT client for test scenarios

### System Dependencies
- Docker (for MQTT broker)
- Python 3.8+
- Node.js (for e2e tests)

## Configuration

### Environment Variables
Create a `.env` file in the `entangled` directory with:

```env
MQTT_USER=your_mqtt_username
MQTT_PASS=your_mqtt_password
PLEX_USER=your_plex_username
PLEX_PASS=your_plex_password
PLEX_RESOURCE=your_plex_client_id
```

### Getting Plex Resource ID
1. Run: `pipenv run python print_all_resources.py`
2. Find your target device in the output
3. Use the ID from `<MyPlexResource:XXXXXXXX>` format

## Usage

### Production Setup
1. Configure environment variables in `.env`
2. Start MQTT broker: `./mqtt/start_mqtt.sh your_password`
3. Start application: `./start_for_prod.sh`
4. Access web interface at `http://localhost:7777`

### Development/Testing
1. Start for e2e tests: `./start_for_e2e.sh`
2. Run unit tests: `pipenv run pytest`
3. Run e2e tests: `cd e2eTests && npm test`

## Known Issues & TODOs

### Issues in Code
1. **Timeline Null Handling** (`plex.py:105`)
   - `self.resource.timeline.time` can be None when movie is paused
   - Needs error handling and fallback logic

2. **Environment Configuration** (`server.py:21-22`)
   - Hard-coded delay configuration for different environments
   - Should use proper environment-based configuration

3. **Plex Connection Lifecycle** (`plex.py:78`)
   - Missing proper connection management methods
   - Should implement `connect_to_account` and `connect_to_resource` methods

### Missing Features
1. **Pause/Resume Synchronization**
   - Currently only handles play commands
   - Should support pause/resume coordination

2. **Multiple Media Type Support**
   - Currently focused on movies
   - Should support TV shows, music, etc.

3. **User Interface Improvements**
   - Basic single-button interface
   - Could benefit from richer controls

4. **Error Handling**
   - Limited error handling for network issues
   - No retry logic for failed connections

5. **Configuration Management**
   - Mix of environment variables and hard-coded values
   - Should use centralized configuration system

## Security Considerations

1. **MQTT Security**
   - Uses password authentication
   - Supports SSL/TLS encryption
   - Passwords stored in plain text files (should use secrets management)

2. **Plex Authentication**
   - Credentials stored in environment variables
   - Direct username/password authentication (should use tokens)

3. **Web Interface**
   - No authentication on web interface
   - Should implement access controls for production use

## Development Notes

The project uses a test-driven development approach with:
- Unit tests for core functionality
- Integration tests for MQTT and Plex components
- End-to-end tests for complete user workflows
- Mock implementations for isolated testing

The architecture is designed for extensibility with abstract base classes and dependency injection patterns.