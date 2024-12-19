from qgis.core import (
    QgsVectorLayer,
    QgsSymbol,
    QgsField,
    QgsProject,
    QgsCategorizedSymbolRenderer,
    QgsRendererCategory,
)
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor
from qgis.utils import iface

# Path to the buildings dataset 
buildings_path = r'C:\Users\raisul\Downloads\Plugin Task\Building data\Building.shp'

# Load the vector layer from the shapefile
building_layer = iface.addVectorLayer(buildings_path, 'Buildings', 'ogr') #org is a file format, part of GDAL library

# Check if the layer is valid
if not building_layer.isValid():
    print("Error: Please check the file path and format")
else:
    # Add a new field to store the number of neighbors
    building_layer.startEditing()
    neighbor_field = QgsField("NNeighbors", QVariant.Int)
    building_layer.addAttribute(neighbor_field)

    # Create a dictionary to store neighbor counts
    neighbor_counts = {feature.id(): 0 for feature in building_layer.getFeatures()} #Dictionary

    # Count neighbors for each building
    for feature in building_layer.getFeatures():
        # Get the geometry of the current building
        current_geom = feature.geometry()
        
        # Check for intersections with other buildings
        for neighbor in building_layer.getFeatures():
            if feature.id() != neighbor.id() and current_geom.intersects(neighbor.geometry()):
                neighbor_counts[feature.id()] += 1

    # Update the field with neighbor counts
    for building_id, count in neighbor_counts.items():
        building_layer.changeAttributeValue(building_id, building_layer.fields().indexFromName("NNeighbors"), count)

    # Commit changes after editing
    building_layer.commitChanges()

    # Set up symbols for rendering
    symbols = {
        "No_Neighbor": QgsSymbol.defaultSymbol(building_layer.geometryType()),
        "One_Neighbor": QgsSymbol.defaultSymbol(building_layer.geometryType()),
        "Multiple_Neighbors": QgsSymbol.defaultSymbol(building_layer.geometryType()),
    }
    symbols["No_Neighbor"].setColor(QColor('yellow'))
    symbols["One_Neighbor"].setColor(QColor('blue'))
    symbols["Multiple_Neighbors"].setColor(QColor('red'))

    # Create categories for rendering based on neighbor counts
    categories = [
        QgsRendererCategory(0, symbols["No_Neighbor"], 'No_Neighbor'),
        QgsRendererCategory(1, symbols["One_Neighbor"], 'One_Neighbor'),
        QgsRendererCategory(2, symbols["Multiple_Neighbors"], 'Two or More Neighbors'),
    ]

    # Apply categorized renderer using the "NumNeighbors" field
    categorized_renderer = QgsCategorizedSymbolRenderer('NNeighbors', categories)
    building_layer.setRenderer(categorized_renderer)

    # Refresh the map canvas and update the view
    iface.mapCanvas().setExtent(building_layer.extent())
    iface.mapCanvas().refresh()

    # Add the updated layer to the current QGIS project
    QgsProject.instance().addMapLayer(building_layer)

    print("Done")
