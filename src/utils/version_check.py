#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Version checking utilities
"""

import os
import json
import time
import urllib.request
import urllib.error
from datetime import datetime

# Current version
VERSION = "0.1.0"

# URL for version checking (this is a placeholder - replace with actual URL when available)
VERSION_CHECK_URL = "https://modsee.net/api/version_check.json"

# Cache timeout in seconds (24 hours)
CACHE_TIMEOUT = 86400


def get_latest_version(force_check=False):
    """
    Check for the latest version of Modsee
    
    Args:
        force_check (bool): Force a check even if cache is valid
        
    Returns:
        tuple: (latest_version, is_update_available, version_info)
    """
    # Get cache directory
    cache_dir = os.path.join(os.path.expanduser("~"), ".modsee")
    os.makedirs(cache_dir, exist_ok=True)
    
    cache_file = os.path.join(cache_dir, "version_cache.json")
    
    # Check if we have a cached version
    if not force_check and os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
                
            # Check if cache is still valid
            cache_time = datetime.fromisoformat(cache_data.get("timestamp", "2000-01-01T00:00:00"))
            current_time = datetime.now()
            time_diff = (current_time - cache_time).total_seconds()
            
            if time_diff < CACHE_TIMEOUT:
                # Cache is still valid
                latest_version = cache_data.get("latest_version", VERSION)
                return latest_version, _compare_versions(VERSION, latest_version), cache_data
                
        except (json.JSONDecodeError, KeyError, ValueError):
            # Cache is invalid, proceed with check
            pass
    
    # Perform online check
    try:
        # Add request timeout to avoid hanging
        response = urllib.request.urlopen(VERSION_CHECK_URL, timeout=3)
        data = response.read().decode('utf-8')
        version_info = json.loads(data)
        
        # Get the latest version
        latest_version = version_info.get("latest_version", VERSION)
        
        # Cache the result
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "latest_version": latest_version,
            "download_url": version_info.get("download_url", ""),
            "release_notes": version_info.get("release_notes", ""),
            "critical_update": version_info.get("critical_update", False)
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)
            
        return latest_version, _compare_versions(VERSION, latest_version), cache_data
        
    except (urllib.error.URLError, json.JSONDecodeError, KeyError, ConnectionError) as e:
        # Can't reach the server or invalid response, return current version
        return VERSION, False, {"error": str(e)}


def _compare_versions(current, latest):
    """
    Compare version strings
    
    Args:
        current (str): Current version
        latest (str): Latest version
        
    Returns:
        bool: True if update is available
    """
    # Split versions into components (assuming semantic versioning)
    try:
        current_parts = [int(x) for x in current.split('.')]
        latest_parts = [int(x) for x in latest.split('.')]
        
        # Pad shorter version with zeros
        while len(current_parts) < len(latest_parts):
            current_parts.append(0)
        while len(latest_parts) < len(current_parts):
            latest_parts.append(0)
            
        # Compare each component
        for c, l in zip(current_parts, latest_parts):
            if l > c:
                return True
            if c > l:
                return False
                
        # Versions are equal
        return False
        
    except ValueError:
        # If we can't parse the versions, assume no update
        return False


if __name__ == "__main__":
    # Test the version check
    latest, update_available, info = get_latest_version(force_check=True)
    print(f"Current version: {VERSION}")
    print(f"Latest version: {latest}")
    print(f"Update available: {update_available}")
    print(f"Version info: {info}") 