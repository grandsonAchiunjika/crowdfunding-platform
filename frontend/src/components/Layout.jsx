import { Box } from "@chakra-ui/react";
import Navbar from "./Navbar"; // Your existing navbar
import Footer from "./Footer";

const Layout = ({ children }) => {
  return (
    <Box minH="100vh" display="flex" flexDirection="column">
      <Navbar />
      <Box flex="1" px={6} py={4}>
        {children}
      </Box>
      <Footer />
    </Box>
  );
};

export default Layout;
