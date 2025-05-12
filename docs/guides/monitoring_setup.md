# Monitoring Setup Guide

## Overview

This document outlines the steps to set up monitoring for the AI Marketing System.

## Key Metrics to Monitor

### Virtual Machine (VM)

- CPU Utilization
- Memory Usage
- Disk I/O
- Network Traffic

### Cloud SQL Database
- CPU Utilization
- Memory Usage
- Storage Usage
- Number of Connections
- Replication Lag (if applicable)

## Setup Steps

1. Navigate to the Google Cloud Console.

2. Find the Monitoring service.

3. Create a new dashboard.

4. Add widgets for the metrics listed above, selecting the appropriate resources (e.g., your VM instance, your Cloud SQL instance).

5. Configure alerting for critical thresholds (e.g., high CPU usage, low disk space).
