import logo from './logo.svg';
import './App.css';
import image1 from './assets/Ambulance.jpg';
import image2 from './assets/Trump.avif';

function App() {
  return (
    <div className="App">
      <header className="App-header">

      <div className="images-container">
          <img src={image1} alt="Image 1" className="header-image" />
          <img src={image2} alt="Image 2" className="header-image" />
        </div>
        
      <h1>
      📰 Newsference 📻
      </h1>
        
       
      </header>
    </div>
  );
}

export default App;
