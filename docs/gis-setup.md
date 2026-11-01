# GIS Database Setup

## Database Configuration
- PostgreSQL: 17.4
- PostGIS: 3.6.2
- Database: smart_parking

## Spatial Tables

### parking_zones
- Stores parking zone information.
- Geometry type: POLYGON
- SRID: 4326

### parking_slots
- Stores individual parking slot information.
- Geometry type: POINT
- SRID: 4326

## Database Migrations
Alembic is configured to manage database schema changes.
The vehicle, parking zone, and parking slot tables have been created through migrations.

## Current Status
The database supports spatial data storage. Actual campus boundaries and parking slot coordinates have not yet been imported.

## Next Steps
1. Establish the relationship between parking zones and parking slots.
2. Integrate campus map data using QGIS and GeoJSON.
3. Store actual spatial geometries in PostGIS.
