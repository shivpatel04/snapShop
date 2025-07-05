import React from "react";
import "./ResultsTable.css";

const ResultsTable = ({ data }) => {
  return (
    <div className="results-grid">
      {data.map((item, i) => (
        <div className="product-card" key={i}>
          {item.image && (
            <img
              src={item.image}
              alt={item.title}
              className="product-image"
            />
          )}
          <h3>{item.title}</h3>
          <p className="price">{item.price}</p>
          <p className="rating">{item.rating}</p>
          <p className="source">{item.source}</p>
          {item.link && (
            <a
              href={item.link}
              className="buy-button"
              target="_blank"
              rel="noopener noreferrer"
            >
              View Product
            </a>
          )}
        </div>
      ))}
    </div>
  );
};

export default ResultsTable;
