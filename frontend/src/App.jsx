import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/home";
import CampaignList from "./pages/CampaignList";
import CampaignDetail from "./pages/CampaignDetail";
import CreateCampaign from "./pages/CreateCampaign";
import Profile from "./pages/Profile";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/campaigns" element={<CampaignList />} />
        <Route path="/campaign/:id" element={<CampaignDetail />} />
        <Route path="/create" element={<CreateCampaign />} />
        <Route path="/profile" element={<Profile />} />
      </Routes>
    </Router>
  );
};

export default App;
