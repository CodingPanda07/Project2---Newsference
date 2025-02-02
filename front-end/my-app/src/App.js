import logo from './logo.svg';
import './App.css';
import image1 from './assets/Ambulance.jpg';
import image2 from './assets/Trump.avif';
import image3 from './assets/War.webp';
import image4 from './assets/Stocks.jpg';
import { useState } from "react";

function App() {
  const [showFilters, setShowFilters] = useState(false);

  const handleSearch = () => {
    setShowFilters(true); 
  };


  return (
    <div className="App">
      <header className="App-header">

      <div className="images-container">
          <img src={image1} alt="Image 1" className="header-image" />
          <img src={image2} alt="Image 2" className="header-image" />
        </div>

        <div className="images-container-right">
          <img src={image3} alt="Image 3" className="header-image" />
          <img src={image4} alt="Image 3" className="header-image" />
        </div>
        
      <h1>
      📰 Newsference 📻
      </h1>

      <h2>
        Welcome to Newsference, a site dedicated to analyzing and understanding our news and business cycles. Search any topic below
        and get detailed metrics about how it is being covered.
      </h2>

      <div className="search-bar-container">
          <input 
            type="text" 
            className="search-bar" 
            placeholder="Search a Topic" 
          />
            <button className="enter-button" onClick={handleSearch}>Enter</button> {}
        </div>

        {showFilters && (
          <div className="filter-buttons">
            <button className="filter-button left">Left</button>
            <button className="filter-button center">Center</button>
            <button className="filter-button right">Right</button>
          </div>
        )}
        
       
      </header>
    </div>
  );
}

export default App;
