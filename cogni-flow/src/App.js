import './App.css';
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

function App() {
  return (
   <Router>
     <div className="app">
      <Routes>
        <Route path="/checkout">
          <h1>checkout</h1>
        </Route>
        <Route path="/login">
          <h1>login page</h1>
        </Route>
        {/* This is the default route*/}
        <Route path="/">
          <h1>Home Page</h1>
        </Route>
      </Routes>
    </div>
   </Router>
  );
}

export default App;