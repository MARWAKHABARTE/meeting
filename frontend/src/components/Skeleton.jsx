import React from "react";

/**
 * Composant Skeleton Loading — affiche des blocs animés pendant le chargement.
 */
export const Skeleton = ({ width = "100%", height = "16px", borderRadius = "6px", className = "" }) => (
  <div
    className={`skeleton ${className}`}
    style={{ width, height, borderRadius }}
    aria-busy="true"
    aria-label="Chargement..."
  />
);

export const SkeletonCard = () => (
  <div className="skeleton-card">
    <Skeleton height="20px" width="60%" />
    <Skeleton height="14px" width="40%" />
    <Skeleton height="14px" width="80%" />
    <Skeleton height="36px" />
  </div>
);

export const SkeletonTable = ({ rows = 5 }) => (
  <div className="skeleton-table">
    {Array.from({ length: rows }).map((_, i) => (
      <div key={i} className="skeleton-row">
        <Skeleton height="14px" width="30%" />
        <Skeleton height="14px" width="20%" />
        <Skeleton height="14px" width="15%" />
        <Skeleton height="28px" width="80px" borderRadius="20px" />
      </div>
    ))}
  </div>
);

export default Skeleton;
