import logo from "./logo.svg";
import "./App.css";
import GetData from "./pages/GetData";
import UploadFile from "./pages/UploadFile";

function App() {
  return (
    <div className="App">
      <GetData />
      <UploadFile />
    </div>
  );
}

export default App;
