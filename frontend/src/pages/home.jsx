import { Box, Text, Button } from "@chakra-ui/react";
import Layout from "../components/Layout";

const Home = () => {
  return (
    <Layout>
      <Box textAlign="center" py={10}>
        <Text fontSize="3xl" fontWeight="bold">Welcome to the Crowdfunding Platform</Text>
        <Text mt={3} fontSize="lg">Empower projects, support dreams, and make an impact.</Text>
        <Button mt={5} colorScheme="blue" size="lg">Explore Campaigns</Button>
      </Box>
    </Layout>
  );
};

export default Home;
