"""
SpatialExtent Domain Object

A SpatialExtent is a weakly semanticised spatial support — geometry
with minimal semantics, allowing platial meaning to emerge from encounters.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shapely.geometry import shape, mapping
from shapely.geometry.base import BaseGeometry

from chora.core.types import NodeType, EpistemicLevel, ExtentId
from chora.core.node import PlatialNode


@dataclass
class SpatialExtent(PlatialNode):
    """
    A weakly semanticised spatial support.
    
    SpatialExtent represents the spatial dimension of place without
    imposing strong semantic categories. Place meaning emerges through
    encounters rather than being predefined.
    
    Parameters
    ----------
    name : str
        Human-readable name (optional, minimal semantics).
    geometry : BaseGeometry | None
        Shapely geometry representing the spatial extent.
    extent_type : str
        Loose classification (e.g., "area", "path", "point").
    semantic_hints : dict[str, Any]
        Optional weak semantic hints (not definitive categories).
    
    Examples
    --------
    >>> from shapely.geometry import Point, Polygon
    >>> 
    >>> # A location point
    >>> cafe = SpatialExtent(
    ...     name="Corner Cafe",
    ...     geometry=Point(-0.1276, 51.5074),
    ...     extent_type="point"
    ... )
    >>> 
    >>> # An area polygon
    >>> park = SpatialExtent(
    ...     name="Hyde Park",
    ...     geometry=Polygon([...]),
    ...     extent_type="area",
    ...     semantic_hints={"land_use": "recreation"}
    ... )
    """
    
    name: str = ""
    geometry: BaseGeometry | None = None
    extent_type: str = "area"
    extent_id: ExtentId | None = None
    semantic_hints: dict[str, Any] = field(default_factory=dict)
    
    # Set node_type
    node_type: NodeType = field(default=NodeType.SPATIAL_EXTENT, init=False)
    
    def __post_init__(self) -> None:
        pass
    
    def __repr__(self) -> str:
        geom_type = self.geometry.geom_type if self.geometry else "None"
        return f"SpatialExtent(id={self.id!r}, name={self.name!r}, geom={geom_type})"
    
    @property
    def has_geometry(self) -> bool:
        """Check if geometry is defined."""
        return self.geometry is not None
    
    @property
    def centroid(self) -> tuple[float, float] | None:
        """Get the centroid coordinates (lon, lat)."""
        if self.geometry is None:
            return None
        c = self.geometry.centroid
        return (c.x, c.y)
    
    @property
    def area_m2(self) -> float | None:
        """Get area in square meters (approximate for geographic coords)."""
        if self.geometry is None:
            return None
        # Note: This is a rough approximation for WGS84
        return self.geometry.area
    
    @property
    def bounds(self) -> tuple[float, float, float, float] | None:
        """Get bounding box (minx, miny, maxx, maxy)."""
        if self.geometry is None:
            return None
        return self.geometry.bounds
    
    def contains_point(self, lon: float, lat: float) -> bool:
        """Check if a point is within this extent."""
        if self.geometry is None:
            return False
        from shapely.geometry import Point
        return self.geometry.contains(Point(lon, lat))
    
    def intersects(self, other: SpatialExtent) -> bool:
        """Check if this extent intersects another."""
        if self.geometry is None or other.geometry is None:
            return False
        return self.geometry.intersects(other.geometry)
    
    def distance_to(self, other: SpatialExtent) -> float | None:
        """Calculate distance to another extent (in geometry units)."""
        if self.geometry is None or other.geometry is None:
            return None
        return self.geometry.distance(other.geometry)
    
    def buffer(self, distance: float) -> SpatialExtent:
        """Create a new extent buffered by the given distance."""
        if self.geometry is None:
            return SpatialExtent(name=f"{self.name} (buffered)")
        return SpatialExtent(
            name=f"{self.name} (buffered)",
            geometry=self.geometry.buffer(distance),
            extent_type=self.extent_type,
            semantic_hints=self.semantic_hints.copy()
        )
    
    def set_hint(self, key: str, value: Any) -> None:
        """Set a semantic hint."""
        self.semantic_hints[key] = value
    
    def get_hint(self, key: str, default: Any = None) -> Any:
        """Get a semantic hint."""
        return self.semantic_hints.get(key, default)
    
    def to_geojson(self) -> dict[str, Any] | None:
        """Export geometry as GeoJSON."""
        if self.geometry is None:
            return None
        return {
            "type": "Feature",
            "geometry": mapping(self.geometry),
            "properties": {
                "id": str(self.id),
                "name": self.name,
                "extent_type": self.extent_type,
                **self.semantic_hints
            }
        }
    
    @classmethod
    def from_geojson(cls, geojson: dict[str, Any]) -> SpatialExtent:
        """Create from GeoJSON feature."""
        props = geojson.get("properties", {})
        geom = shape(geojson["geometry"]) if "geometry" in geojson else None
        return cls(
            name=props.get("name", ""),
            geometry=geom,
            extent_type=props.get("extent_type", "area"),
            semantic_hints={k: v for k, v in props.items() 
                          if k not in ("id", "name", "extent_type")}
        )
    
    @classmethod
    def point(cls, lon: float, lat: float, name: str = "") -> SpatialExtent:
        """Create a point extent."""
        from shapely.geometry import Point
        return cls(name=name, geometry=Point(lon, lat), extent_type="point")
    
    @classmethod
    def from_bounds(cls, minx: float, miny: float, maxx: float, maxy: float,
                    name: str = "") -> SpatialExtent:
        """Create an extent from bounding box."""
        from shapely.geometry import box
        return cls(name=name, geometry=box(minx, miny, maxx, maxy), extent_type="area")
