// frontend/src/components/DraggableResizeBar.jsx
import React from 'react';
import './DraggableResizeBar.css';

const DraggableResizeBar = ({ onMouseDown }) => {
  return (
    <div
      className="drag-bar"
      onMouseDown={onMouseDown}
    />
  );
};

export default DraggableResizeBar;