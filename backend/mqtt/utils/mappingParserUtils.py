import logging
import json
from typing import Dict, List, Tuple
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import backend.models.models as models
from backend.extensions import db

# Todo: correct error logging for non existing devices
def parse_mapping_payload(payload):
    """
    Parse the mapping payload from MQTT message.
    
    Args:
        payload: JSON string
        
    Returns:
        List[Dict]: Parsed mapping data or None if parsing fails
        
    Expected payload structure:
    [
        {
            "uuid_actuator": "ffc3307b-618e-11f0-ba83-ac50dee21cb3",
            "uuid_sensor": "ffc33079-618e-11f0-bffe-ac50dee21cb3", 
            "impact_factor": 10.0,
            "actuator_can_increases_sensor": true,
            "actuator_can_decreases_sensor": true,
            "only_physical": false,
            "active_influences": 0
        },
        <...>
    ]
    """
    try:
        if not payload:
            logging.warning("Empty mapping payload received")
            return None
            
        # Parse JSON payload
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in mapping payload: {str(e)}")
            return None
        
        if not isinstance(data, list):
            logging.error("Mapping payload is not a JSON array")
            return None
        
        parsed_mappings = []
        for i, mapping in enumerate(data):
            if not isinstance(mapping, dict):
                logging.warning(f"Mapping entry {i} is not a JSON object, skipping")
                continue
                
            # Validate required fields
            required_fields = ['uuid_actuator', 'uuid_sensor', 'impact_factor', 
                             'actuator_can_increases_sensor', 'actuator_can_decreases_sensor']
            
            if not all(field in mapping for field in required_fields):
                logging.warning(f"Mapping entry {i} missing required fields, skipping")
                continue
            
            # Extract and validate the mapping data
            try:
                parsed_mapping = {
                    'uuid_actuator': str(mapping['uuid_actuator']),
                    'uuid_sensor': str(mapping['uuid_sensor']),
                    'impact_factor': float(mapping['impact_factor']),
                    'actuator_can_increases_sensor': bool(mapping['actuator_can_increases_sensor']),
                    'actuator_can_decreases_sensor': bool(mapping['actuator_can_decreases_sensor']),
                    'only_physical': bool(mapping.get('only_physical', False)),
                    'active_influences': int(mapping.get('active_influences', 0))
                }
                
                # Validate impact factor
                if parsed_mapping['impact_factor'] <= 0:
                    logging.warning(f"Invalid impact factor {parsed_mapping['impact_factor']} in mapping {i}, skipping")
                    continue
                
                # Validate that at least one influence type is true
                if not (parsed_mapping['actuator_can_increases_sensor'] or parsed_mapping['actuator_can_decreases_sensor']):
                    logging.warning(f"Mapping {i} has no influence types enabled, skipping")
                    continue
                
                parsed_mappings.append(parsed_mapping)
                
            except (ValueError, TypeError) as e:
                logging.warning(f"Error parsing mapping entry {i}: {str(e)}, skipping")
                continue
        
        logging.info(f"Successfully parsed {len(parsed_mappings)} sensor-actuator mappings")
        return parsed_mappings if parsed_mappings else None
        
    except Exception as e:
        logging.error(f"Error parsing mapping payload: {str(e)}")
        return None


def create_or_update_sensor_actuator_mappings(app, mappings):
    """
    Create or update sensor-actuator mappings in the database with proper race condition handling.
    
    Args:
        app: Flask application instance
        mappings (List[Dict]): List of parsed mapping dictionaries
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with app.app_context():
            created_count = 0
            updated_count = 0
            failed_count = 0
            
            for i, mapping in enumerate(mappings):
                logging.debug(f"Processing mapping {i+1}/{len(mappings)}: {mapping['uuid_actuator']} -> {mapping['uuid_sensor']}")
                
                try:
                    # Process each mapping in its own transaction to handle race conditions
                    success = _process_single_mapping(mapping)
                    if success == 'created':
                        created_count += 1
                        logging.debug(f"Successfully created mapping {i+1}")
                    elif success == 'updated':
                        updated_count += 1
                        logging.debug(f"Successfully updated mapping {i+1}")
                    else:
                        failed_count += 1
                        logging.warning(f"Failed to process mapping {i+1}")
                        
                except Exception as e:
                    logging.error(f"Error processing mapping {i+1} {mapping.get('uuid_actuator')} -> {mapping.get('uuid_sensor')}: {str(e)}")
                    failed_count += 1
                    # Ensure clean session state for next iteration
                    try:
                        db.session.rollback()
                    except:
                        pass
                    continue
            
            # Try to link any mappings that now have corresponding devices
            linked_count = link_mappings_to_devices(app)
            
            logging.info(f"Mapping operation completed: {created_count} created, {updated_count} updated, "
                        f"{failed_count} failed, {linked_count} linked to devices")
            
            return failed_count == 0
            
    except Exception as e:
        logging.error(f"Error creating/updating sensor-actuator mappings: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass
        return False


def _process_single_mapping(mapping):
    """
    Process a single mapping with proper race condition handling.
    
    Args:
        mapping (dict): Single mapping dictionary
        
    Returns:
        str: 'created', 'updated', or 'failed'
    """
    try:
        # Start with a fresh session state
        try:
            db.session.commit()  # Commit any pending changes
        except:
            db.session.rollback()  # If commit fails, rollback
        
        # Check if mapping already exists
        existing_mapping = models.SensorActuatorMapping.query.filter_by(
            uuid_actuator=mapping['uuid_actuator'],
            uuid_sensor=mapping['uuid_sensor']
        ).first()
        
        if existing_mapping:
            # Update existing mapping
            _update_mapping_from_data(existing_mapping, mapping)
            db.session.commit()
            logging.debug(f"Updated mapping: {mapping['uuid_actuator']} -> {mapping['uuid_sensor']}")
            return 'updated'
        else:
            # Try to create new mapping with race condition handling
            try:
                new_mapping = _create_mapping_from_data(mapping)
                db.session.add(new_mapping)
                db.session.commit()
                logging.debug(f"Created mapping: {mapping['uuid_actuator']} -> {mapping['uuid_sensor']}")
                return 'created'
                
            except IntegrityError as ie:
                # Handle race condition - mapping was created by another process
                db.session.rollback()
                logging.info(f"Mapping {mapping['uuid_actuator']} -> {mapping['uuid_sensor']} "
                           f"was created by another process, attempting to update")
                
                # Try to fetch and update the mapping that was created by another process
                existing_mapping = models.SensorActuatorMapping.query.filter_by(
                    uuid_actuator=mapping['uuid_actuator'],
                    uuid_sensor=mapping['uuid_sensor']
                ).first()
                
                if existing_mapping:
                    _update_mapping_from_data(existing_mapping, mapping)
                    db.session.commit()
                    logging.debug(f"Updated mapping after race condition: {mapping['uuid_actuator']} -> {mapping['uuid_sensor']}")
                    return 'updated'
                else:
                    logging.error(f"Failed to retrieve mapping after integrity error: {mapping['uuid_actuator']} -> {mapping['uuid_sensor']}")
                    return 'failed'
                    
    except Exception as e:
        logging.error(f"Error processing single mapping {mapping.get('uuid_actuator')} -> {mapping.get('uuid_sensor')}: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass
        return 'failed'


def _create_mapping_from_data(mapping):
    """Create a new SensorActuatorMapping object from parsed data"""
    return models.SensorActuatorMapping(
        uuid_actuator=mapping['uuid_actuator'],
        uuid_sensor=mapping['uuid_sensor'],
        impact_factor=mapping['impact_factor'],
        actuator_can_increases_sensor=mapping['actuator_can_increases_sensor'],
        actuator_can_decreases_sensor=mapping['actuator_can_decreases_sensor'],
        only_physical=mapping['only_physical'],
        active_influences=mapping['active_influences']
    )


def _update_mapping_from_data(existing_mapping, mapping):
    """Update an existing SensorActuatorMapping object with new data"""
    existing_mapping.impact_factor = mapping['impact_factor']
    existing_mapping.actuator_can_increases_sensor = mapping['actuator_can_increases_sensor']
    existing_mapping.actuator_can_decreases_sensor = mapping['actuator_can_decreases_sensor']
    existing_mapping.only_physical = mapping['only_physical']
    existing_mapping.active_influences = mapping['active_influences']
    existing_mapping.updated_at = datetime.utcnow()


def link_mappings_to_devices(app) -> int:
    """
    Link existing mappings to devices that have been created.
    
    Args:
        app: Flask application instance
        
    Returns:
        int: Number of mappings successfully linked
    """
    try:
        with app.app_context():
            # Get all mappings that don't have device links yet
            unlinked_mappings = models.SensorActuatorMapping.query.filter(
                (models.SensorActuatorMapping.actuator_device_id.is_(None)) |
                (models.SensorActuatorMapping.sensor_device_id.is_(None))
            ).all()
            
            linked_count = 0
            
            for mapping in unlinked_mappings:
                updated = False
                
                # Try to link actuator device
                if mapping.actuator_device_id is None:
                    actuator_device = models.Device.query.filter_by(device_id=mapping.uuid_actuator).first()
                    if actuator_device:
                        mapping.actuator_device_id = actuator_device.id
                        updated = True
                        logging.debug(f"Linked actuator {mapping.uuid_actuator} to mapping")
                
                # Try to link sensor device
                if mapping.sensor_device_id is None:
                    sensor_device = models.Device.query.filter_by(device_id=mapping.uuid_sensor).first()
                    if sensor_device:
                        mapping.sensor_device_id = sensor_device.id
                        updated = True
                        logging.debug(f"Linked sensor {mapping.uuid_sensor} to mapping")
                
                if updated:
                    mapping.updated_at = datetime.utcnow()
                    linked_count += 1
            
            if linked_count > 0:
                db.session.commit()
                logging.info(f"Successfully linked {linked_count} mappings to devices")
            
            return linked_count
            
    except Exception as e:
        logging.error(f"Error linking mappings to devices: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass
        return 0


def get_actuator_sensor_matrices(app=None) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """
    Build actuator-sensor mapping matrices from database.
    
    Args:
        app: Flask application instance (optional, uses current_app if None)
        
    Returns:
        - actuator_increases_sensor_mapping_matrix: {'a1': ['s1', 's2'], 'a2': ['s2']}
        - actuator_decreases_sensor_mapping_matrix: {'a1': ['s1']}
    """
    try:
        # If app is provided, use it; otherwise use current_app (for API routes)
        if app:
            with app.app_context():
                return _get_matrices()
        else:
            from flask import current_app
            with current_app.app_context():
                return _get_matrices()
            
    except Exception as e:
        logging.error(f"Error generating actuator-sensor matrices: {str(e)}")
        return {}, {}


def _get_matrices():
    """Helper function to get matrices within app context"""
    # Get all active mappings with linked devices
    mappings = models.SensorActuatorMapping.query.filter(
        models.SensorActuatorMapping.actuator_device_id.isnot(None),
        models.SensorActuatorMapping.sensor_device_id.isnot(None)
    ).all()
    
    increases_matrix = {}
    decreases_matrix = {}
    
    for mapping in mappings:
        actuator_uuid = mapping.uuid_actuator
        sensor_uuid = mapping.uuid_sensor
        
        # Build increases matrix
        if mapping.actuator_can_increases_sensor:
            if actuator_uuid not in increases_matrix:
                increases_matrix[actuator_uuid] = []
            if sensor_uuid not in increases_matrix[actuator_uuid]:
                increases_matrix[actuator_uuid].append(sensor_uuid)
        
        # Build decreases matrix
        if mapping.actuator_can_decreases_sensor:
            if actuator_uuid not in decreases_matrix:
                decreases_matrix[actuator_uuid] = []
            if sensor_uuid not in decreases_matrix[actuator_uuid]:
                decreases_matrix[actuator_uuid].append(sensor_uuid)
    
    logging.debug(f"Generated mapping matrices: {len(increases_matrix)} actuators with increase mappings, "
                 f"{len(decreases_matrix)} actuators with decrease mappings")
    
    return increases_matrix, decreases_matrix


def get_mapping_impact_factors(app=None) -> Dict[str, float]:
    """
    Get impact factors for all actuator-sensor pairs.
    
    Args:
        app: Flask application instance (optional, uses current_app if None)
        
    Returns:
        Dict mapping "actuator_uuid:sensor_uuid" strings to impact factors
    """
    try:
        # If app is provided, use it; otherwise use current_app (for API routes)
        if app:
            with app.app_context():
                return _get_impact_factors()
        else:
            from flask import current_app
            with current_app.app_context():
                return _get_impact_factors()
            
    except Exception as e:
        logging.error(f"Error retrieving mapping impact factors: {str(e)}")
        return {}


def _get_impact_factors():
    """Helper function to get impact factors within app context"""
    mappings = models.SensorActuatorMapping.query.filter(
        models.SensorActuatorMapping.actuator_device_id.isnot(None),
        models.SensorActuatorMapping.sensor_device_id.isnot(None)
    ).all()
    
    impact_factors = {}
    for mapping in mappings:
        # Use string key instead of tuple
        key = f"{mapping.uuid_actuator}:{mapping.uuid_sensor}"
        impact_factors[key] = mapping.impact_factor
    
    logging.debug(f"Retrieved impact factors for {len(impact_factors)} actuator-sensor pairs")
    return impact_factors