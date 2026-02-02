"""
H3 Spatial Indexing for Chora

Hexagonal hierarchical spatial index using Uber's H3 library.
Provides efficient spatial queries and multi-resolution place representation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, Any

from chora.core.types import NodeType, ExtentId
from chora.core.node import PlatialNode
from chora.core.spatial_extent import SpatialExtent


@dataclass
class H3SpatialExtent(SpatialExtent):
    """
    A SpatialExtent backed by H3 hexagonal cells.
    
    H3 provides:
    - Hierarchical resolution (0-15, where 15 is ~1m²)
    - Efficient neighbor queries
    - Consistent sizing across the globe
    
    Parameters
    ----------
    h3_index : str
        The H3 cell index string.
    resolution : int
        H3 resolution level (0-15).
    """
    
    h3_index: str = ""
    resolution: int = 9  # ~174m edge length
    
    def __post_init__(self) -> None:
        """Initialize geometry from H3 index if not provided."""
        if self.h3_index and self.geometry is None:
            self.geometry = h3_to_polygon(self.h3_index)
    
    @classmethod
    def from_h3(cls, h3_index: str, name: str = "") -> H3SpatialExtent:
        """Create from H3 index string."""
        try:
            import h3
            res = h3.get_resolution(h3_index)
        except ImportError:
            raise ImportError("h3 package not installed. Run: pip install h3")
        
        return cls(
            h3_index=h3_index,
            resolution=res,
            name=name or f"h3:{h3_index[:8]}",
            geometry=h3_to_polygon(h3_index),
            extent_type="hexagon"
        )
    
    @classmethod
    def from_point_h3(
        cls, 
        lon: float, 
        lat: float, 
        resolution: int = 9,
        name: str = ""
    ) -> H3SpatialExtent:
        """Create H3 extent from a point at given resolution."""
        try:
            import h3
        except ImportError:
            raise ImportError("h3 package not installed. Run: pip install h3")
        
        h3_index = h3.latlng_to_cell(lat, lon, resolution)
        return cls.from_h3(h3_index, name)
    
    @property
    def neighbors(self) -> list[str]:
        """Get neighboring H3 cell indices."""
        try:
            import h3
            return list(h3.grid_ring(self.h3_index, 1))
        except ImportError:
            return []
    
    @property
    def parent(self) -> str | None:
        """Get parent cell at coarser resolution."""
        if self.resolution == 0:
            return None
        try:
            import h3
            return h3.cell_to_parent(self.h3_index, self.resolution - 1)
        except ImportError:
            return None
    
    @property
    def children(self) -> list[str]:
        """Get child cells at finer resolution."""
        if self.resolution >= 15:
            return []
        try:
            import h3
            return list(h3.cell_to_children(self.h3_index, self.resolution + 1))
        except ImportError:
            return []
    
    def k_ring(self, k: int = 1) -> list[str]:
        """Get all cells within k rings of this cell."""
        try:
            import h3
            return list(h3.grid_disk(self.h3_index, k))
        except ImportError:
            return [self.h3_index]
    
    def distance_to_h3(self, other: H3SpatialExtent) -> int:
        """Get grid distance to another H3 cell."""
        try:
            import h3
            return h3.grid_distance(self.h3_index, other.h3_index)
        except (ImportError, ValueError):
            return -1


# =============================================================================
# Utility Functions
# =============================================================================

def h3_to_polygon(h3_index: str):
    """Convert H3 index to Shapely polygon."""
    try:
        import h3
        from shapely.geometry import Polygon
        
        boundary = h3.cell_to_boundary(h3_index)
        # H3 returns (lat, lng) pairs, need to flip to (lng, lat)
        coords = [(lng, lat) for lat, lng in boundary]
        return Polygon(coords)
    except ImportError:
        return None


def point_to_h3(lon: float, lat: float, resolution: int = 9) -> str:
    """Convert a point to H3 cell index."""
    try:
        import h3
        return h3.latlng_to_cell(lat, lon, resolution)
    except ImportError:
        raise ImportError("h3 package not installed. Run: pip install h3")


def extent_to_h3(
    extent: SpatialExtent, 
    resolution: int = 9
) -> list[str]:
    """
    Convert a SpatialExtent to covering H3 cells.
    
    For polygons, returns all cells that intersect the geometry.
    For points, returns the single containing cell.
    """
    try:
        import h3
    except ImportError:
        raise ImportError("h3 package not installed. Run: pip install h3")
    
    if extent.geometry is None:
        return []
    
    geom = extent.geometry
    
    if geom.geom_type == "Point":
        return [h3.latlng_to_cell(geom.y, geom.x, resolution)]
    
    elif geom.geom_type == "Polygon":
        # Use polyfill to get all cells
        coords = list(geom.exterior.coords)
        # H3 expects (lat, lng) pairs
        h3_coords = [(lat, lng) for lng, lat in coords]
        try:
            return list(h3.polygon_to_cells(h3.Polygon(h3_coords), resolution))
        except Exception:
            # Fallback: just use centroid
            c = geom.centroid
            return [h3.latlng_to_cell(c.y, c.x, resolution)]
    
    else:
        # For other geometries, use centroid
        c = geom.centroid
        return [h3.latlng_to_cell(c.y, c.x, resolution)]


def h3_to_extent(h3_index: str, name: str = "") -> H3SpatialExtent:
    """Convert H3 index to H3SpatialExtent."""
    return H3SpatialExtent.from_h3(h3_index, name)


def compact_h3_cells(cells: list[str]) -> list[str]:
    """Compact a set of H3 cells to minimal representation."""
    try:
        import h3
        return list(h3.compact_cells(cells))
    except ImportError:
        return cells


def uncompact_h3_cells(cells: list[str], resolution: int) -> list[str]:
    """Uncompact H3 cells to specified resolution."""
    try:
        import h3
        return list(h3.uncompact_cells(cells, resolution))
    except ImportError:
        return cells


# =============================================================================
# Resolution Guide
# =============================================================================

H3_RESOLUTION_GUIDE = {
    0: "~1107 km edge, continental",
    1: "~418 km edge, large country",
    2: "~158 km edge, region",
    3: "~59 km edge, metropolitan area",
    4: "~22 km edge, large city",
    5: "~8 km edge, city district",
    6: "~3 km edge, neighborhood",
    7: "~1.2 km edge, large block",
    8: "~461 m edge, city block",
    9: "~174 m edge, building cluster",
    10: "~65 m edge, building",
    11: "~24 m edge, small building",
    12: "~9 m edge, room",
    13: "~3.2 m edge, desk",
    14: "~1.2 m edge, person",
    15: "~0.5 m edge, very precise"
}


def resolution_for_scale(scale: str) -> int:
    """Get appropriate H3 resolution for a named scale."""
    scale_mapping = {
        "continental": 0,
        "country": 1,
        "region": 2,
        "metro": 3,
        "city": 4,
        "district": 5,
        "neighborhood": 6,
        "block": 8,
        "building": 10,
        "room": 12,
        "precise": 15
    }
    return scale_mapping.get(scale.lower(), 9)
